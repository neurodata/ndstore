import unittest

from tgscheduler import (start_scheduler, stop_scheduler, add_single_task,
    add_interval_task, add_monthly_task, add_weekly_task, add_cron_like_task,
    cancel, get_task, get_tasks, rename_task)


def functest(*args, **kws):
    pass


class TestScheduler(unittest.TestCase):

    def setUp(self):
        self.sched = start_scheduler()

    def tearDown(self):
        stop_scheduler()

    def test_running(self):
        """Test that the scheduler is running."""
        self.assertTrue(hasattr(self.sched, 'running'), "no running attribute")
        self.assertTrue(self.sched.running, "scheduler is not running")


class TestTasks(unittest.TestCase):

    def test_single_task(self):
        """Test adding a single task."""
        task = add_single_task(functest, taskname='singletest')
        self.assertEqual(task.action, functest)
        self.assertEqual(task.name, 'singletest')

    def test_weekly_task(self):
        """Test adding a weekly task."""
        task = add_weekly_task(
            functest, [2], (0, 0), taskname='weekdaytest')
        self.assertEqual(task.action, functest)
        self.assertEqual(task.name, 'weekdaytest')

    def test_monthly_task(self):
        """Test adding a monthly task."""
        task = add_monthly_task(
            functest, (2, 10), (1, 0), taskname='monthlytest')
        self.assertEqual(task.action, functest)
        self.assertEqual(task.name, 'monthlytest')

    def test_interval_task(self):
        """Test adding an interval task."""
        task = add_interval_task(functest, 60*10, taskname='intervaltest')
        self.assertEqual(task.action, functest)
        self.assertEqual(task.name, 'intervaltest')

    def test_cron_like_task(self):
        """Test adding a simple cron-like task."""
        task = add_cron_like_task(functest, '* * * * *', taskname='every_minute')
        self.assertEqual(task.action, functest)
        self.assertEqual(task.name, 'every_minute')
        self.assertEqual(task.minutes, range(0, 60),
            "Invalid minutes: %s" % task.minutes)
        self.assertEqual(task.hours, range(0, 24),
            "Invalid hours: %s" % task.hours)
        self.assertEqual(task.doms, range(1, 32),
            "Invalid doms: %s" % task.doms)
        self.assertEqual(task.months, range(1, 13),
            "Invalid months: %s" % task.months)
        self.assertEqual(task.dows, range(0, 7),
            "Invalid dows: %s" % task.dows)

    def test_cron_like_business_hours(self):
        """Test a crontab for business hours."""
        task = add_cron_like_task(functest, '*/30 8-12,14-18 * * MON-FRI',
            taskname='crontest_business_hours')
        self.assertEqual(task.action, functest)
        self.assertEqual(task.name, 'crontest_business_hours')
        self.assertEqual(task.minutes, [0, 30],
            "Invalid minutes: %s" % task.minutes)
        self.assertEqual(task.hours, [8, 9, 10, 11, 12, 14, 15, 16, 17, 18],
            "Invalid hours: %s" % task.hours)
        self.assertEqual(task.doms, range(1, 32),
            "Invalid doms: %s" % task.doms)
        self.assertEqual(task.months, range(1, 13),
            "Invalid months: %s" % task.months)
        self.assertEqual(task.dows, range(0, 5),
            "Invalid dows: %s" % task.dows)

    def test_cron_like_complex(self):
        """Test a more complex crontab."""
        task = add_cron_like_task(functest,
            '5-10,25-30,57 8-12,14-18 2,25-28 Jan-mar,10-12 SuN-wEd',
            taskname='crontest_complex')
        self.assertEqual(task.action, functest)
        self.assertEqual(task.name, 'crontest_complex')
        self.assertEqual(task.minutes,
            [5, 6, 7, 8, 9, 10, 25, 26, 27, 28, 29, 30, 57],
            "Invalid minutes: %s" % task.minutes)
        self.assertEqual(task.hours, [8, 9, 10, 11, 12, 14, 15, 16, 17, 18],
            "Invalid hours: %s" % task.hours)
        self.assertEqual(task.doms, [2, 25, 26, 27, 28],
            "Invalid doms: %s" % task.doms)
        self.assertEqual(task.months, [1, 2, 3, 10, 11, 12],
            "Invalid months: %s" % task.months)
        self.assertEqual(task.dows, [0, 1, 2, 6],
            "Invalid dows: %s" % task.dows)

    def test_cron_like_failure(self):
        """Test with an invalid crontab.

        This test should fail with ValueError as we feed the scheduler with
        an incorrect value: `Jan-12` (mixing names and integers is not supported)

        """
        self.assertRaises(ValueError, add_cron_like_task,
            functest, '* * * Jan-12 *', taskname='crontest3')

    def test_duplicate_task(self):
        """Test adding a task with the same name as an existing task."""
        add_single_task(functest, taskname='duplicate')
        self.assertRaises(ValueError, add_single_task,
            functest, taskname='duplicate')

    def test_rename_task(self):
        """Test renaming a single task."""
        task = add_single_task(functest, taskname='footask')
        self.assertEqual(task.name, 'footask')
        self.assertEqual(get_task('footask'), task)
        self.assertTrue(get_task('bartask') is None)
        self.assertTrue('footask' in get_tasks())
        self.assertTrue('bartask' not in get_tasks())
        rename_task('footask', 'bartask')
        self.assertEqual(task.name, 'bartask')
        self.assertTrue(get_task('footask') is None)
        self.assertEqual(get_task('bartask'), task)
        self.assertTrue('footask' not in get_tasks())
        self.assertTrue('bartask' in get_tasks())

    def test_cancel_task(self):
        """Test to cancel a task."""
        task = add_single_task(functest, taskname='badtask')
        self.assertEqual(task.name, 'badtask')
        self.assertEqual(get_task('badtask'), task)
        self.assertTrue('badtask' in get_tasks())
        cancel(task)
        self.assertTrue(get_task('badtask') is None)
        self.assertTrue('badtask' not in get_tasks())

    def test_cancel_task_by_name(self):
        """Test to cancel a task using its taskname."""
        task = add_single_task(functest, taskname='badtask')
        self.assertEqual(task.name, 'badtask')
        self.assertEqual(get_task('badtask'), task)
        self.assertTrue('badtask' in get_tasks())
        cancel('badtask')
        self.assertTrue(get_task('badtask') is None)
        self.assertTrue('badtask' not in get_tasks())

    def test_cancel_task_not_exists(self):
        """Test to cancel a task that does not exist."""
        self.assertTrue(get_task('badtask') is None)
        self.assertTrue('badtask' not in get_tasks())
        cancel('badtask')
        self.assertTrue(get_task('badtask') is None)
        self.assertTrue('badtask' not in get_tasks())


if __name__ == '__main__':
    unittest.main()

