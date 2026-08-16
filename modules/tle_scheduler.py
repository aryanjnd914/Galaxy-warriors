"""
modules/tle_scheduler.py
Scheduled TLE Updates — fetches fresh data from CelesTrak every hour
automatically without restarting the server.
Uses APScheduler (lightweight, no cron needed on Windows).
Install: pip install apscheduler
"""

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import logging

# Suppress APScheduler logs unless error
logging.getLogger('apscheduler').setLevel(logging.ERROR)

_scheduler = None
_last_update = None
_update_count = 0


def start_scheduler(fetch_fn, score_fn, app_state: dict, interval_minutes=60):
    """
    Start background scheduler that refreshes TLE data every hour.

    fetch_fn   — your fetch_live_tle function
    score_fn   — your score_debris function
    app_state  — dict with keys '_debris' and '_scored' to update in place
    interval_minutes — how often to refresh (default 60 min)
    """
    global _scheduler, _last_update, _update_count

    def refresh_job():
        global _last_update, _update_count
        try:
            print(f"\n[SCHEDULER] Auto-refreshing TLE data at {datetime.utcnow().strftime('%H:%M UTC')}...")
            fresh_debris = fetch_fn()
            fresh_scored = score_fn(fresh_debris)

            # Update shared app state in place
            app_state['_debris'] = fresh_debris
            app_state['_scored'] = fresh_scored

            _last_update = datetime.utcnow()
            _update_count += 1

            print(f"[SCHEDULER] Refresh #{_update_count} complete — {len(fresh_scored)} objects updated")

        except Exception as e:
            print(f"[SCHEDULER] Refresh failed: {e}")

    _scheduler = BackgroundScheduler(timezone='UTC')
    _scheduler.add_job(
        refresh_job,
        trigger='interval',
        minutes=interval_minutes,
        id='tle_refresh',
        name='TLE Auto-Refresh',
        replace_existing=True
    )
    _scheduler.start()
    _last_update = datetime.utcnow()
    print(f"[SCHEDULER] TLE auto-refresh started — every {interval_minutes} minutes")
    return _scheduler


def stop_scheduler():
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown()
        print("[SCHEDULER] Stopped")


def get_status():
    """Returns scheduler status for the /api/scheduler_status endpoint."""
    global _last_update, _update_count, _scheduler
    return {
        "running": _scheduler.running if _scheduler else False,
        "last_update": _last_update.strftime("%Y-%m-%d %H:%M UTC") if _last_update else "Never",
        "update_count": _update_count,
        "next_update": _scheduler.get_jobs()[0].next_run_time.astimezone(__import__("pytz").utc).strftime("%H:%M UTC")
                       if _scheduler and _scheduler.get_jobs() else "Unknown"
    }
