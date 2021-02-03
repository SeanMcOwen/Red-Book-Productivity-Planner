import os
import unittest
from flask import Flask,request, render_template
import sqlite3
import pandas as pd
from Create_Databases import excel_to_db
import RedBook, RedBookBokeh

from threading import Thread
from tornado.ioloop import IOLoop
import numpy as np
from bokeh.embed import server_document

from bokeh.server.server import Server
from bs4 import BeautifulSoup

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
    

    def test_case1(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        response = self.app.get('/Create/Goals', follow_redirects=True)        
        self.assertIn("Please create a group before creating goals.", str(response.data))
        
        
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
        
        
        response = self.app.get('/Create/Goals', follow_redirects=True)        
        self.assertIn("Please create a progress object before creating goals.", str(response.data))
        
        
        response = self.app.get('Create/Progress', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        response = self.app.post(
          '/Create/Progress',
          data = dict(progress_name="Read Book 1",
                      progress_type="Progress",
                      units=1,
                      starting_value=0),
          follow_redirects=True
          )
        self.assertEqual(response.status_code, 200)
        
        response = self.app.post(
          '/Create/Progress',
          data = dict(progress_name="Read Book 2",
                      progress_type="Progress",
                      units=1,
                      starting_value=20),
          follow_redirects=True
          )
        self.assertEqual(response.status_code, 200)
        
        progress_values = pd.read_sql("SELECT * FROM progress", conn)[["Goal Name", "Value"]].values
        expected = np.array([['Read Book 1',0.0], ['Read Book 2', 20.0]], dtype=object)
        self.assertEqual((progress_values == expected).all().all(), True)

        progress_values = pd.read_sql("SELECT * FROM progress_params", conn).values
        expected = np.array([['Read Book 1', 1.0, 'Progress'],
                             ['Read Book 2', 1.0,'Progress']], dtype=object)
        self.assertEqual((progress_values == expected).all().all(), True)
        
        response = self.app.get('/Create/Goals', follow_redirects=True)     
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.data, 'html.parser')
        
        progress_name_select = soup.find("select", attrs={"id": "progress_name_select"})
        progress_name_select = progress_name_select.find_all('option')
        progress_name_select = [x.text for x in progress_name_select]
        self.assertEqual(progress_name_select, ['Read Book 1', 'Read Book 2'])
        
        group_name_select = soup.find("select", attrs={"id": "group_name_select"})
        group_name_select = group_name_select.find_all('option')
        group_name_select = [x.text for x in group_name_select]
        self.assertEqual(group_name_select, ['Projects', 'Reading'])        
        
        
        
        
if __name__ == "__main__":
    unittest.main()
    