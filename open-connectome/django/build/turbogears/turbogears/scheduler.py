"""Module that provides a cron-like task scheduler."""

__all__ = ['add_cron_like_task', 'add_interval_task', 'add_monthday_task',
    'add_monthly_task', 'add_single_task', 'add_weekday_task',
    'add_weekly_task', 'cancel', 'get_task', 'get_tasks',
    'rename_task', 'start_scheduler', 'stop_scheduler']

from tgscheduler.scheduler import (add_cron_like_task, add_interval_task,
    add_monthday_task, add_monthly_task, add_single_task,
    add_weekday_task, add_weekly_task, cancel, get_task, get_tasks,
    rename_task, start_scheduler, stop_scheduler)
