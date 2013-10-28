"""The TurboGears scheduler package.

You can schedule Python functions to be called at specific intervals or days.
The scheduler uses the standard sched module for the actual task scheduling,
but provides much more:

    * Repeated (at intervals, or on specific days).
    * Error handling (exceptions in your tasks don't kill the scheduler).
    * You can run the scheduler in its own thread or a separate process.
    * You can run a task in its own thread or a separate process.

"""

from scheduler import (add_interval_task, add_monthday_task, add_monthly_task,
    add_single_task, add_weekday_task, add_weekly_task, add_cron_like_task,
    cancel, get_task, get_tasks, rename_task, start_scheduler, stop_scheduler)
