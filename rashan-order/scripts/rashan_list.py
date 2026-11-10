#!/usr/bin/env python3
"""Rashan list manager: the single source of truth for what the household needs.

Data lives in one JSON file: $RASHAN_DIR/list.json (default ~/.rashan-order/list.json).
Every command accepts --json for machine-readable output.

  add NAME [--qty "2 kg"] [--brand X] [--note X] [--every DAYS]
  remove ID_OR_NAME
  list                      everything on the list
  due                       what should be ordered now
  ordered [--ids 1,2] --store S [--order-id X] [--total N]
  history [-n 5]
  config [KEY [VALUE]]      keys: store, budget, address_label, upi_id, price_jump_pct
"""
import argparse, json, os, sys, tempfile
from datetime import date, datetime

DIR = os.path.expanduser(os.environ.get("RASHAN_DIR", "~/.rashan-order"))
PATH = os.path.join(DIR, "list.json")
CONFIG_KEYS = {"store": str, "budget": float, "address_label": str, "upi_id": str, "price_jump_pct": float}
DEFAULT = {"config": {"store": "blinkit", "budget": None, "address_label": None,
                      "upi_id": None, "price_jump_pct": 20.0},
           "next_id": 1, "items": [], "history": []}


def load():
    if not os.path.exists(PATH):
        return json.loads(json.dumps(DEFAULT))
    try:
        with open(PATH, encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError("top level is not an object")
    except (ValueError, OSError) as e:
        # Refuse to continue: silently starting a fresh list would wipe the household's data on next save.
        sys.exit(f"cannot read {PATH}: {e}\nFix or rename that file, then run again.")
    for k, v in DEFAULT.items():
        data.setdefault(k, json.loads(json.dumps(v)))
    for k, v in DEFAULT["config"].items():
        data["config"].setdefault(k, v)
    return data


def save(data):
    os.makedirs(DIR, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=DIR, suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, PATH)  # atomic: a crash never leaves a half-written list


def today_date():
    override = os.environ.get("RASHAN_TODAY")  # for tests
    return date.fromisoformat(override) if override else date.today()


def is_due(item, today):
    if not item.get("every_days"):
        return True  # one-time items stay due until ordered
    last = item.get("last_ordered")
    if not last:
        return True
    try:
        return (today - date.fromisoformat(last)).days >= item["every_days"]
    except (ValueError, TypeError):
        return True  # unreadable date: better to offer the item than to hide it forever


def fmt(item):
    parts = [f"[{item['id']}] {item['name']}"]
    if item.get("qty"):
        parts.append(f"x {item['qty']}")
    if item.get("brand"):
        parts.append(f"({item['brand']})")
    if item.get("every_days"):
        parts.append(f"- every {item['every_days']}d, last: {item.get('last_ordered') or 'never'}")
    if item.get("note"):
        parts.append(f"- note: {item['note']}")
    return " ".join(parts)


def out(args, payload, lines):
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print("\n".join(lines) if lines else "(empty)")


def find(data, key):
    if key.isdigit():
        return [i for i in data["items"] if i["id"] == int(key)]
    return [i for i in data["items"] if i["name"].lower() == key.lower()]


def main():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add", parents=[common])
    a.add_argument("name"); a.add_argument("--qty"); a.add_argument("--brand")
    a.add_argument("--note"); a.add_argument("--every", type=int, metavar="DAYS")
    r = sub.add_parser("remove", parents=[common]); r.add_argument("key")
    sub.add_parser("list", parents=[common])
    sub.add_parser("due", parents=[common])
    o = sub.add_parser("ordered", parents=[common])
    o.add_argument("--ids", help="comma-separated ids; default: everything currently due")
    o.add_argument("--store", required=True); o.add_argument("--order-id"); o.add_argument("--total", type=float)
    o.add_argument("--dry-run", action="store_true", help="show what would be recorded, change nothing")
    h = sub.add_parser("history", parents=[common]); h.add_argument("-n", type=int, default=5)
    c = sub.add_parser("config", parents=[common]); c.add_argument("key", nargs="?"); c.add_argument("value", nargs="?")

    for stream in (sys.stdout, sys.stderr):  # Hindi item names must print on Windows consoles too
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    args = p.parse_args()
    data = load()
    today = today_date()

    if args.cmd == "add":
        if args.every is not None and args.every < 1:
            sys.exit("--every must be at least 1 day")
        args.name = " ".join(args.name.split())
        if not args.name:
            sys.exit("item name cannot be empty")
        if args.name.isdigit():
            sys.exit("item name cannot be only a number (numbers are used as ids)")
        dup = find(data, args.name)
        if dup:  # same name again means "update it", not "buy it twice"
            item = dup[0]
            for k, v in (("qty", args.qty), ("brand", args.brand), ("note", args.note), ("every_days", args.every)):
                if v is not None:
                    item[k] = v
            msg = "updated"
        else:
            item = {"id": data["next_id"], "name": args.name, "qty": args.qty, "brand": args.brand,
                    "note": args.note, "every_days": args.every, "last_ordered": None, "added": today.isoformat()}
            data["next_id"] += 1
            data["items"].append(item)
            msg = "added"
        save(data)
        out(args, {"status": msg, "item": item}, [f"{msg}: {fmt(item)}"])

    elif args.cmd == "remove":
        hits = find(data, args.key)
        if not hits:
            sys.exit(f"no item matching '{args.key}'")
        data["items"] = [i for i in data["items"] if i not in hits]
        save(data)
        out(args, {"removed": hits}, [f"removed: {fmt(i)}" for i in hits])

    elif args.cmd == "list":
        out(args, {"items": data["items"], "config": data["config"]}, [fmt(i) for i in data["items"]])

    elif args.cmd == "due":
        due = [i for i in data["items"] if is_due(i, today)]
        out(args, {"due": due, "config": data["config"]}, [fmt(i) for i in due])

    elif args.cmd == "ordered":
        if args.ids:
            try:
                ids = {int(x) for x in args.ids.split(",") if x.strip()}
            except ValueError:
                sys.exit("--ids must be comma-separated numbers")
            done = [i for i in data["items"] if i["id"] in ids]
            missing = ids - {i["id"] for i in done}
            if missing:
                sys.exit(f"unknown ids: {sorted(missing)}")
        else:
            done = [i for i in data["items"] if is_due(i, today)]
        if not done:
            sys.exit("nothing to mark as ordered")
        entry = {"date": datetime.now().isoformat(timespec="minutes"), "store": args.store,
                 "order_id": args.order_id, "total": args.total,
                 "items": [{"name": i["name"], "qty": i.get("qty"), "brand": i.get("brand")} for i in done]}
        if args.dry_run:
            out(args, {"would_record": entry}, [f"would record {len(done)} item(s) from {args.store}"])
            return
        data["history"].append(entry)
        for i in done:
            if i.get("every_days"):
                i["last_ordered"] = today.isoformat()  # recurring: stays, comes due again later
        data["items"] = [i for i in data["items"] if i not in done or i.get("every_days")]
        save(data)
        out(args, {"recorded": entry}, [f"recorded {len(done)} item(s) from {args.store}"])

    elif args.cmd == "history":
        recent = data["history"][-args.n:]
        lines = [f"{e['date']} {e['store']} total={e.get('total')} id={e.get('order_id')}: "
                 + ", ".join(x["name"] for x in e["items"]) for e in recent]
        out(args, {"history": recent}, lines)

    elif args.cmd == "config":
        if args.key is None:
            out(args, data["config"], [f"{k} = {v}" for k, v in data["config"].items()])
            return
        if args.key not in CONFIG_KEYS:
            sys.exit(f"unknown key; choose from {sorted(CONFIG_KEYS)}")
        if args.value is not None:
            try:
                val = None if args.value.lower() in ("none", "") else CONFIG_KEYS[args.key](args.value)
            except ValueError:
                sys.exit(f"{args.key} must be a number")
            if isinstance(val, float) and not (0 < val < float("inf")):
                sys.exit(f"{args.key} must be a positive number")
            data["config"][args.key] = val
            save(data)
        out(args, {args.key: data["config"][args.key]}, [f"{args.key} = {data['config'][args.key]}"])


if __name__ == "__main__":
    main()
