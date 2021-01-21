import os
import unittest
from flask import Flask,request, render_template
import sqlite3
import pandas as pd
from Create_Databases import excel_to_db
import RedBook, RedBookBokeh

from threading import Thread
from tornado.ioloop import IOLoop
from bokeh.embed import server_document

from bokeh.server.server import Server


from RedBookFlask import app

database_name = 'Goals.db'


class BasicTests(unittest.TestCase):
 
    ############################
    #### setup and teardown ####
    ############################
 
    # executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = True
        self.app = app.test_client()
        
        for csv in ['Completed.csv',
         'Goals.csv',
         'Group.csv',
         'Habits Progress.csv',
         'Habits.csv',
         'progress_params.csv',
         'project_log.csv',
         'Tasks.csv']:
            if csv in os.listdir("."):
                os.rename(csv, "_"+csv)
        assert len([x for x in os.listdir(".") if ".csv" in x and x[0] != "_"]) == 0
        
        if "Goals.db" in os.listdir("."):
            os.rename("Goals.db" , "_Goals.db")
    #Add in a way to copy over and save the excel files so they aren't overwritten
 
    # executed after each test
    def tearDown(self):
        for csv in ['Completed.csv',
         'Goals.csv',
         'Group.csv',
         'Habits Progress.csv',
         'Habits.csv',
         'progress_params.csv',
         'project_log.csv',
         'Tasks.csv']:
            if csv in os.listdir("."):
                os.remove(csv)
        if "Goals.db" in os.listdir("."):
            os.remove("Goals.db")
        for csv in ['_Completed.csv',
         '_Goals.csv',
         '_Group.csv',
         '_Habits Progress.csv',
         '_Habits.csv',
         '_progress_params.csv',
         '_project_log.csv',
         '_Tasks.csv']:
            if csv in os.listdir("."):
                os.rename(csv, csv[1:])
        if "_Goals.db" in os.listdir("."):
            os.rename("_Goals.db" , "Goals.db")
    
    def test_main_page(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        
    
    def test_group_create_page(self):
        response = self.app.get('/Create/Group', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        response = self.app.post(
          '/Create/Group',
          data = dict(group_name="Projects"),
          follow_redirects=True
          )
        self.assertEqual(response.status_code, 200)
        
        
        response = self.app.post(
          '/Create/Group',
          data = dict(group_name="Reading"),
          follow_redirects=True
          )
        self.assertEqual(response.status_code, 200)
        
        
        with sqlite3.connect(database_name) as conn:
            groups = list(pd.read_sql("SELECT * FROM groups", conn)['Group'].values)
        self.assertEqual(groups, ["Projects", "Reading"])
        

        
        
        
if __name__ == "__main__":
    unittest.main()
    