# Scheduling the order job

## What to ask the user

- When: day(s) and time, in their time zone. Suggest a time they are usually home and awake, because a quick-commerce order arrives minutes after they approve it.
- Whether staples should be recurring items (`--every DAYS`) so the scheduled run has something to pick up without anyone adding it each time.

## What the scheduled run does

Give the scheduled task a self-contained instruction, because it may start with no memory of this conversation. For example:

> Use the rashan-order skill. Run `rashan_list.py due --json`. If nothing is due, finish quietly. Otherwise build the cart on the configured store and send me the final-verification summary. Do not place the order or start payment until I reply yes to that summary.

The run must end at the final-verification summary. The order is placed only when the user replies yes; with no reply nothing is bought. If the environment can send a push notification or message, use it for the summary so the user sees it on their phone.

## Which scheduler

Use what the current environment provides, in this order of preference:

1. A built-in scheduled-task / routine feature of the Claude app in use (desktop app scheduled tasks, cloud scheduled tasks, `/loop` or cron tools in Claude Code).
2. If there is none, tell the user there is no scheduler here and offer the manual trigger: they say "rashan order kar do" whenever they want.

Two things must be true for a scheduled order to work, so check them and tell the user if either is missing:

- The scheduled run needs the same browser tool, signed in to the store. A cloud run cannot see a browser on a computer that is switched off.
- The run must read the same `list.json` the user adds items to. If the scheduler starts in a fresh environment, put `RASHAN_DIR` somewhere that persists and is shared.

To change or stop the schedule, edit or delete the scheduled task and confirm to the user what is now set.
