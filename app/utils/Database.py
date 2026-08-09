import time
import logging
from django.db import connection

logger = logging.getLogger("app.database")


def retry_db_operation(func, max_retries=3, base_delay=1.0):
    last_exception = None
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            last_exception = e
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                logger.warning("DB operation failed (attempt %d/%d): %s. Retrying in %.1fs...",
                               attempt + 1, max_retries, e, delay)
                time.sleep(delay)
    raise last_exception


class Database(object):
    def __init__(self, logger):
        self.logger = logger

    def select(self, sql, params=None):
        """Execute SELECT query with optional parameterized params.
        WARNING: Always use params for user-provided values to prevent SQL injection.
        """
        data = []

        def _execute():
            cursor = connection.cursor()
            try:
                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)
                rawData = cursor.fetchall()
                col_names = [desc[0] for desc in cursor.description]
                result = []
                for row in rawData:
                    d = {}
                    for index, value in enumerate(row):
                        d[col_names[index]] = value
                    result.append(d)
                return result
            finally:
                cursor.close()

        try:
            data = retry_db_operation(_execute)
        except Exception as e:
            self.logger.error("Database.select() error:%s,sql:%s" % (str(e), sql))
            raise

        return data

    def execute(self, sql, params=None):
        """Execute SQL command with optional parameterized params.
        WARNING: Always use params for user-provided values to prevent SQL injection.
        """
        ret = False

        def _execute():
            cursor = connection.cursor()
            try:
                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)
                return True
            finally:
                cursor.close()

        try:
            ret = retry_db_operation(_execute)
        except Exception as e:
            self.logger.error("Database.execute() error:%s,sql:%s" % (str(e), sql))
        return ret
