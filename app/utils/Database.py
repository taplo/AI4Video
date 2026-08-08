from django.db import connection

class Database(object):
    def __init__(self, logger):
        self.logger = logger

    def select(self, sql):
        data = []
        cursor = connection.cursor()
        cursor.execute(sql)
        try:
            rawData = cursor.fetchall()
            col_names = [desc[0] for desc in cursor.description]
            for row in rawData:
                d = {}
                for index, value in enumerate(row):
                    d[col_names[index]] = value
                data.append(d)
        except Exception as e:
            self.logger.error("Database.select() error:%s,sql:%s" % (str(e),sql))

        return data

    def execute(self, sql):
        ret = False
        try:
            cursor = connection.cursor()
            cursor.execute(sql)
            ret = True
        except Exception as e:
            self.logger.error("Database.execute() error:%s,sql:%s" % (str(e), sql))
        return ret
