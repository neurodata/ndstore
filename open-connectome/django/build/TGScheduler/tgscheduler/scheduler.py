"""Create the scheduler object and expose its method as functions."""

import kronos
from kronos import method
import atexit
import logging

log = logging.getLogger(__name__)


class Scheduler(object):
    """Handle Task Scheduling."""

    def __init__(self):
        self._scheduler_instance = None

    def start_scheduler(self):
        """Start the scheduler and register shutdown at exit."""
        log.info("Starting the scheduler...")
        si = self._get_scheduler()
        si.start()
        atexit.register(self.stop_scheduler)
        return si

    def stop_scheduler(self):
        """Stop the scheduler."""
        log.info("Shutting down the scheduler...")
        if not self._scheduler_instance:
            return
        si = self._get_scheduler()
        si.stop()

    def _get_scheduler(self):
        """Find the best available scheduler."""
        if not self._scheduler_instance:
            if hasattr(kronos, 'ThreadedScheduler'):
                log.debug("Using threaded scheduler")
                self._scheduler_instance = kronos.ThreadedScheduler()
            elif hasattr(kronos, 'ForkedScheduler'):
                log.debug("Using Forked scheduler")
                self._scheduler_instance = kronos.ForkedScheduler()
            else:
                log.debug("Using Sequential scheduler")
                self._scheduler_instance = kronos.Scheduler()

        return self._scheduler_instance

    def add_interval_task(self, action, interval, args=None, kw=None,
            initialdelay=0, processmethod=method.threaded, taskname=None):
        """Add an interval task to the scheduler.

        Pass in initialdelay with a number of seconds to wait before running and
        an  interval with the number of seconds between runs.

        For example, an initialdelay of 600 and interval of 60 would mean
        "start running after 10 minutes and run every 1 minute after that".

        @param interval: The interval in seconds between executing the action
        @param initaldelay: the initial delay before starting execution

        @param action: The callable that will be called at the time you request
        @param args: Tuple of positional parameters to pass to the action
        @param kw: Keyword arguments to pass to the action
        @param taskname:  Tasks can have a name (stored in task.name), which can
        help if you're trying to keep track of many tasks.
        @param precessmethod: By default, each task will be run in a new thread.
        You can also pass in turbogears.scheduler.method.sequential or
        turbogears.scheduler.method.forked.

        """
        si = self._get_scheduler()
        return si.add_interval_task(action=action, interval=interval, args=args,
            kw=kw, initialdelay=initialdelay, processmethod=processmethod,
            taskname=taskname)

    def add_single_task(self, action, args=None, kw=None,
            initialdelay=0, processmethod=method.threaded, taskname=None):
        """Add a single task to the scheduler.

        Runs a task once. Pass in ``initialdelay`` with a number of seconds
        to wait before running.

        @param initaldelay: the initial delay before starting execution

        @param action: The callable that will be called at the time you request
        @param args: Tuple of positional parameters to pass to the action
        @param kw: Keyword arguments to pass to the action
        @param taskname:  Tasks can have a name (stored in task.name), which can
        help if you're trying to keep track of many tasks.
        @param precessmethod: By default, each task will be run in a new thread.
        You can also pass in turbogears.scheduler.method.sequential or
        turbogears.scheduler.method.forked.

        """
        si = self._get_scheduler()
        return si.add_single_task(action=action, args=args, kw=kw,
            initialdelay=initialdelay, processmethod=processmethod,
            taskname=taskname)

    def add_weekday_task(self, action, weekdays, timeonday, args=None, kw=None,
            processmethod=method.threaded, taskname=None):
        """Add a weekday task to the scheduler.

        Runs on certain days of the week. Pass in a list or tuple of weekdays
        from 1-7 (where 1 is Monday). Additionally, you need to pass in
        timeonday which is the time of day to run. timeonday should be a tuple
        with (hour, minute).

        @param weekdays: list ot tuple of weekdays to execute action
        @param timeonday: tuple (hour, minute), to run on weekday

        @param action: The callable that will be called at the time you request
        @param args: Tuple of positional parameters to pass to the action
        @param kw: Keyword arguments to pass to the action
        @param taskname:  Tasks can have a name (stored in task.name), which can
        help if you're trying to keep track of many tasks.
        @param precessmethod: By default, each task will be run in a new thread.
        You can also pass in turbogears.scheduler.method.sequential or
        turbogears.scheduler.method.forked.

        """
        si = self._get_scheduler()
        return si.add_daytime_task(action=action, taskname=taskname,
            weekdays=weekdays, monthdays=None, timeonday=timeonday,
            processmethod=processmethod, args=args, kw=kw)

    def add_monthday_task(self, action, monthdays, timeonday, args=None, kw=None,
            processmethod=method.threaded, taskname=None):
        """Add a monthly task to the scheduler.

        Runs on certain days of the month. Pass in a list or tuple of monthdays
        from 1-31, import and also pass in timeonday which is an (hour, minute)
         tuple of the time of day to run the task.

        @param monthdays: list ot tuple of monthdays to execute action
        @param timeonday: tuple (hour, minute), to run on monthday

        @param action: The callable that will be called at the time you request
        @param args: Tuple of positional parameters to pass to the action
        @param kw: Keyword arguments to pass to the action
        @param taskname:  Tasks can have a name (stored in task.name), which can
        help if you're trying to keep track of many tasks.
        @param precessmethod: By default, each task will be run in a new thread.
        You can also pass in turbogears.scheduler.method.sequential or
        turbogears.scheduler.method.forked.

        """
        si = self._get_scheduler()
        return si.add_daytime_task(action=action, taskname=taskname,
            weekdays=None, monthdays=monthdays, timeonday=timeonday,
            processmethod=processmethod, args=args, kw=kw)

    def add_cron_like_task(self, action, cron_str, args=None, kw=None,
            processmethod=method.threaded, taskname=None):
        """Add a task to the scheduler based on a cron-like syntax.

        @param cron_str: The scheduling information, written in a cron-like syntax

        @param action: The callable that will be called at the time you request
        @param args: Tuple of positional parameters to pass to the action
        @param kw: Keyword arguments to pass to the action
        @param taskname:  Tasks can have a name (stored in task.name), which can
        help if you're trying to keep track of many tasks.
        @param processmethod: By default, each task will be run in a new thread.
        You can also pass in turbogears.scheduler.method.sequential or
        turbogears.scheduler.method.forked.

        """
        si = self._get_scheduler()
        return si.add_cron_like_task(action=action, taskname=taskname,
            cron_str=cron_str, processmethod=processmethod,
            args=args, kw=kw)

    def get_task(self, taskname):
        """Retrieve a task from the scheduler by task name.

        @param taskname: the name of the task to retrieve

        """
        si = self._get_scheduler()
        return si.tasks.get(taskname)

    def get_tasks(self):
        """Retrieve all tasks from the scheduler."""
        si = self._get_scheduler()
        return si.tasks

    def rename_task(self, taskname, newname):
        """Rename a scheduled task."""
        si = self._get_scheduler()
        si.rename(taskname, newname)

    def cancel(self, task):
        """Cancel task by task name.

        @param task: the task itself or the task.name of the task to cancel

        """
        si = self._get_scheduler()
        if isinstance (task, basestring):
            task = get_task(task)
        if task:
            si.cancel(task)

scheduler = Scheduler()


# backwards compatibility

start_scheduler = scheduler.start_scheduler
stop_scheduler = scheduler.stop_scheduler

add_single_task = scheduler.add_single_task
add_interval_task = scheduler.add_interval_task
add_monthday_task = scheduler.add_monthday_task
add_monthly_task = add_monthday_task # alias
add_weekday_task = scheduler.add_weekday_task
add_weekly_task = add_weekday_task # alias
add_cron_like_task = scheduler.add_cron_like_task

cancel = scheduler.cancel
get_task = scheduler.get_task
get_tasks = scheduler.get_tasks
rename_task = scheduler.rename_task

