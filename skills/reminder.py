# coding: utf-8
#DB-API 2.0 interface for SQLite databases

import sqlite3
import time


def time_str2unix(time_str, fmt="%Y-%m-%d %H:%M:%S"):
    return time.mktime(time.strptime(time_str, fmt))


def time_unix2str(time_unix, fmt="%Y-%m-%d %H:%M:%S"):
    return time.strftime(fmt, time.localtime(time_unix))


class ReminderSqlite(object):

    def __init__(self, path, table):
        self.conn = sqlite3.connect(path)
        self.path = path
        self.table = table
        self.curs = self.conn.cursor()
        self.create()

    def create(self):
        sql_paras = ['PRAGMA foreign_keys=OFF;', 'BEGIN TRANSACTION;']
        sql_paras.append('''
        CREATE TABLE IF NOT EXISTS %s(
            tid INTEGER PRIMARY KEY autoincrement,
            createtime DATETIME DEFAULT (datetime('now', 'localtime')),
            notifytime DATETIME,
            notifyevent TEXT,
            active BOOLEAN DEFAULT 1,
            period INTEGER DEFAULT -1
        );
        ''' % self.table)
        self.conn = sqlite3.connect(self.path)
        self.curs = self.conn.cursor()
        for sql in sql_paras:
            self.curs.execute(sql)
        self.conn.commit()

    def query(self, sql=None):
        if sql is None:
            sql = 'select * from %s' % self.table
        self.curs.execute(sql)
        data = self.curs.fetchall()
        return data

    def query_active(self, sql):
        sql = 'select * from %s where active=1 and active0' % self.table
        self.query(sql)
        return data

    def update(self, sql, data=None):
        if data:
            self.curs.execute(sql, data)
        else:
            self.curs.execute(sql)
        self.conn.commit()

    def handler(self, json_data):
        intent = json_data.get('intent')
        data = json_data.get('data')
        create_time = int(time.time())
        if intent == 'create':
            pass
        elif intent == 'query':
            pass
        elif intent == 'delete':
            pass
        elif intent == 'update':
            pass
        elif intent == 'break':
            pass
        else:
            raise
        event = data.get('event')
        time = data.get('time')
        period = data.get('period')
        data = (time, event, period)
        sql = "INSERT INTO %s(alarmtime, alarmevent, alarmperiod) VALUES (?,?,?)"
        self.insert(sql, data)

    def insert(self, sql, data):
        sql = sql % self.table
        self.curs.execute(sql, data)
        self.conn.commit()

    def drop(self):
        sql = 'DROP TABLE IF EXISTS ' + self.table
        self.curs.execute(sql)
        self.conn.commit()
        self.curs.close()

    def close(self):
        self.curs.close()
        self.conn.close()


if __name__ == '__main__':
    alarm_sql = ReminderSqlite('../db/reminder_test.db', 'reminder')
    alarm_sql.drop()
    alarm_sql.create()
    data = alarm_sql.query()
    print data

    time_str = time_unix2str(time.time() + 3600)

    sql = u"INSERT INTO %s(notifytime, notifyevent, period) VALUES(?,?,?)" % alarm_sql.table
    idata = (time_str, u"下班", -1)
    alarm_sql.insert(sql, idata)
    data = alarm_sql.query()

    for row in data:
        print row
        sql = u"UPDATE %s set active=1 where tid=%s" % (alarm_sql.table, row[0])
        alarm_sql.update(sql)

    data = alarm_sql.query()
    print data
    alarm_sql.close()
