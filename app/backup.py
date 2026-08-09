import os
import sqlite3
import logging
from datetime import datetime, timedelta

from framework.settings import BASE_DIR

logger = logging.getLogger("app.backup")


def backup_database():
    source_db = os.path.join(BASE_DIR, "ai4video.sqlite3")
    backup_dir = os.path.join(BASE_DIR, "backups")
    os.makedirs(backup_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(backup_dir, f"ai4video_{timestamp}.sqlite3")

    try:
        source = sqlite3.connect(source_db)
        dest = sqlite3.connect(backup_file)
        with dest:
            source.backup(dest)
        dest.close()
        source.close()
        logger.info("Database backup created: %s", backup_file)
        cleanup_old_backups(backup_dir, days=7)
    except Exception as e:
        logger.error("Database backup failed: %s", e)


def cleanup_old_backups(backup_dir, days=7):
    cutoff_time = datetime.now() - timedelta(days=days)
    for filename in os.listdir(backup_dir):
        if filename.startswith("ai4video_") and filename.endswith(".sqlite3"):
            filepath = os.path.join(backup_dir, filename)
            file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            if file_time < cutoff_time:
                os.remove(filepath)
                logger.info("Deleted old backup: %s", filepath)
