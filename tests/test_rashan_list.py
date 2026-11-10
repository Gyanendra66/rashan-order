import json, os, subprocess, sys, tempfile, unittest

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "rashan-order", "scripts", "rashan_list.py")


class RashanListTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env = dict(os.environ, RASHAN_DIR=self.tmp.name, RASHAN_TODAY="2026-01-01", PYTHONIOENCODING="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def run_cmd(self, *args, today=None, ok=True):
        env = dict(self.env, RASHAN_TODAY=today) if today else self.env
        r = subprocess.run([sys.executable, SCRIPT, *args], capture_output=True, text=True, encoding="utf-8", env=env)
        if ok:
            self.assertEqual(r.returncode, 0, r.stderr)
        return r

    def due(self, today=None):
        return [i["name"] for i in json.loads(self.run_cmd("due", "--json", today=today).stdout)["due"]]

    def test_add_list_remove(self):
        self.run_cmd("add", "haldi", "--qty", "200 g")
        self.run_cmd("add", "दूध", "--qty", "1 L")
        self.assertEqual(self.due(), ["haldi", "दूध"])
        self.run_cmd("remove", "HALDI")
        self.assertEqual(self.due(), ["दूध"])
        self.assertNotEqual(self.run_cmd("remove", "nope", ok=False).returncode, 0)

    def test_duplicate_updates(self):
        self.run_cmd("add", "atta", "--qty", "5 kg", "--brand", "X")
        self.run_cmd("add", "Atta", "--qty", "10 kg")
        items = json.loads(self.run_cmd("list", "--json").stdout)["items"]
        self.assertEqual(len(items), 1)
        self.assertEqual((items[0]["qty"], items[0]["brand"]), ("10 kg", "X"))

    def test_recurring_and_one_time(self):
        self.run_cmd("add", "atta", "--every", "30")
        self.run_cmd("add", "haldi")
        self.run_cmd("ordered", "--store", "blinkit", "--total", "300")
        self.assertEqual(self.due(), [])
        self.assertEqual(self.due(today="2026-01-30"), [])
        self.assertEqual(self.due(today="2026-01-31"), ["atta"])
        hist = json.loads(self.run_cmd("history", "--json").stdout)["history"]
        self.assertEqual(len(hist[0]["items"]), 2)

    def test_ordered_subset_keeps_rest_due(self):
        self.run_cmd("add", "a1"); self.run_cmd("add", "b1")
        self.run_cmd("ordered", "--ids", "1", "--store", "s")
        self.assertEqual(self.due(), ["b1"])
        self.assertNotEqual(self.run_cmd("ordered", "--ids", "9", "--store", "s", ok=False).returncode, 0)

    def test_dry_run_changes_nothing(self):
        self.run_cmd("add", "a1")
        self.run_cmd("ordered", "--store", "s", "--dry-run")
        self.assertEqual(self.due(), ["a1"])

    def test_bad_input_rejected(self):
        for args in (["add", "  "], ["add", "12"], ["add", "x", "--every", "0"],
                     ["config", "budget", "abc"], ["config", "budget", "-5"], ["config", "nokey", "1"],
                     ["ordered", "--store", "s"]):
            self.assertNotEqual(self.run_cmd(*args, ok=False).returncode, 0, args)

    def test_corrupt_file_is_not_overwritten(self):
        path = os.path.join(self.tmp.name, "list.json")
        with open(path, "w") as f:
            f.write("{broken")
        self.assertNotEqual(self.run_cmd("add", "x", ok=False).returncode, 0)
        with open(path) as f:
            self.assertEqual(f.read(), "{broken")

    def test_config(self):
        self.run_cmd("config", "budget", "1500")
        self.assertEqual(json.loads(self.run_cmd("config", "--json").stdout)["budget"], 1500.0)
        self.run_cmd("config", "budget", "none")
        self.assertIsNone(json.loads(self.run_cmd("config", "--json").stdout)["budget"])


if __name__ == "__main__":
    unittest.main()
