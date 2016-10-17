# -*- coding: utf-8 -*-
# import logging
# import logging.config
import sqlite3
from datetime import datetime

# class Database():
#     def __init__(self):
#         logging.config.fileConfig('logging.conf')
#         self.logger = logging.getLogger('main.Database')

class DBSQLite(Object):

    #create database
    def __init__(self, dbFileName):
        # Database.__init__(self)
        self.cx = sqlite3.connect(dbFileName)
        self.cu = self.cx.cursor()

    def getCursor(self):
        return self.cu

    def commit(self):
        self.cx.commit()

    def ExecQuery(self, sql, parameters, commit=True):
        re = []
        try:
            li = self.cu.execute(sql, parameters).fetchall()
            if(li):
                re = li
        except Exception as e:
            print('An error occurred:', e.args[0])
            # self.logger.error('SQL=' + sql + '. ' + 'parameters=' + str(parameters))
            # self.logger.error(e)
            
        if commit:
            self.commit()
        return re

    def ExecNoQuery(self, sql, parameters):
        try:
            self.cu.execute(sql, parameters)
            #print sql
        except Exception as e:
            print('An error occurred:', e.args[0])
            # self.logger.error(e)
            # self.logger.error('Error: sql=' + sql)
            raise e
