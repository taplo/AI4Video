import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger("app.scheduler")

scheduler = BackgroundScheduler()


def setup_scheduler():
    from app.backup import backup_database
    scheduler.add_job(
        backup_database,
        CronTrigger(hour=2, minute=0),
        id='daily_backup',
        name='Daily database backup',
        replace_existing=True
    )
    scheduler.start()
    logger.info("Scheduler started with daily backup job")
