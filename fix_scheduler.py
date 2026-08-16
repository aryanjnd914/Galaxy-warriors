with open("modules/tle_scheduler.py", "r", encoding="utf-8") as f:
    content = f.read()

# Fix 1: Add UTC timezone to BackgroundScheduler
content = content.replace(
    "_scheduler = BackgroundScheduler()",
    "_scheduler = BackgroundScheduler(timezone='UTC')"
)

# Fix 2: Format next_update correctly
content = content.replace(
    'next_update": _scheduler.get_jobs()[0].next_run_time.strftime("%H:%M UTC")',
    'next_update": _scheduler.get_jobs()[0].next_run_time.astimezone(__import__("pytz").utc).strftime("%H:%M UTC")'
)

with open("modules/tle_scheduler.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Done - scheduler timezone fixed")
