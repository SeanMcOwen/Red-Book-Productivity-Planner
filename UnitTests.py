import os
import unittest
from flask import Flask,request, render_template
import sqlite3
import pandas as pd
from Create_Databases import excel_to_db
import RedBook, RedBookBokeh
from datetime import datetime

from threading import Thread
from tornado.ioloop import IOLoop
import numpy as np
from bokeh.embed import server_document

from bokeh.server.server import Server
from bs4 import BeautifulSoup

from RedBookFlask import app

database_name = 'Goals.db'

def test_connectivity1(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        response = self.app.get('/Create/Goals', follow_redirects=True)        
        self.assertIn("Please create a group before creating goals.", str(response.data))
        
        
        response = self.app.get('/Create/Group', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

def test_connectivity2(self):
    response = self.app.get('/Create/Goals', follow_redirects=True)        
    self.assertIn("Please create a progress object before creating goals.", str(response.data))
        
def check_groups(self, groups1):
    with sqlite3.connect(database_name) as conn:
        groups = list(pd.read_sql("SELECT * FROM groups", conn)['Group'].values)
    self.assertEqual(groups1, groups)

def create_group(self, group):
    response = self.app.post(
          '/Create/Group',
          data = dict(group_name=group),
          follow_redirects=True
          )
    self.assertEqual(response.status_code, 200)
    
def create_check_group(self, groups, groups_add):
    for group in groups_add:
        create_group(self, group)
        groups.append(group)
        check_groups(self, groups)
        
def check_goals_page_widgets(self, progress, groups):
    response = self.app.get('/Create/Goals', follow_redirects=True)     
    self.assertEqual(response.status_code, 200)
    soup = BeautifulSoup(response.data, 'html.parser')
    progress_name_select = soup.find("select", attrs={"id": "progress_name_select"})
    
    progress_name_select = progress_name_select.find_all('option')
    progress_name_select = [x.text for x in progress_name_select]
    self.assertEqual(progress_name_select, list(np.array(progress)[:,0]))
    
    group_name_select = soup.find("select", attrs={"id": "group_name_select"})
    group_name_select = group_name_select.find_all('option')
    group_name_select = [x.text for x in group_name_select]
    self.assertEqual(group_name_select, groups)
    
def check_view_goals_page_widgets(self, goals_list):
    response = self.app.get('/Goals/Goals', follow_redirects=True)     
    self.assertEqual(response.status_code, 200)
    soup = BeautifulSoup(response.data, 'html.parser')
    print(soup)

def create_progress(self, progress, progress_type, units, starting_value):
    response = self.app.post(
          '/Create/Progress',
          data = dict(progress_name=progress,
                      progress_type=progress_type,
                      units=units,
                      starting_value=starting_value),
          follow_redirects=True
          )
    self.assertEqual(response.status_code, 200)
    
    
def create_check_progress(self, progress, progress_params, progress_add):
    for p in progress_add:
        temp = [self] + p
        create_progress(*temp)
        progress.append([temp[1], temp[4]])
        progress_params.append([temp[1], temp[3], temp[2], ""])
        check_progress_log(self, np.array(progress, dtype=object))
        check_progress_params(self, np.array(progress_params, dtype=object))
        
def check_progress_log(self, expected):
    with sqlite3.connect(database_name) as conn:
        progress_values = pd.read_sql("SELECT * FROM progress", conn)[["Goal Name", "Value"]].values
    self.assertEqual((progress_values == expected).all().all(), True)
    
    
def check_progress_params(self, expected):
    with sqlite3.connect(database_name) as conn:
        progress_values = pd.read_sql("SELECT * FROM progress_params", conn).values
    self.assertEqual((progress_values == expected).all(), True)
    
def create_goal(self, goal, goals_list, active_goals):
    response = self.app.post(
          '/Create/Goals',
          data = goal,
          follow_redirects=True
          )
    self.assertEqual(response.status_code, 200)
    if goal['start_date'] >= today:
        active_goals.append(goal)
    goals_list.append(goal)
    
today = pd.to_datetime(datetime.today().date())
goals_to_add = []
goals_to_add.append(dict(goal_name = 'Read Book 2',
                      group_name_select = "Reading",
                      progress_name_select = 'Read Book 2',
                      end_progress = 500,
                      start_date = (today + pd.Timedelta("10D")).date(),
                      end_date = (today + pd.Timedelta("50D")).date(),
                      today = 1,
            week= 1,
            month =  1,
            quarter = 1,
            year = 1,
            historical = 1))
        
goals_to_add.append(dict(goal_name = 'Read Book 1',
                      group_name_select = "Reading",
                      progress_name_select = 'Read Book 1',
                      end_progress = 300,
                      start_date = (today).date(),
                      end_date = (today + pd.Timedelta("50D")).date(),
                      today = 1,
            week= 1,
            month =  1,
            quarter = 1,
            year = 1,
            historical = 1))
        

goals_to_add.append(dict(goal_name = '100 Hours Yoga',
                      group_name_select = "Exercise",
                      progress_name_select = "Practice Yoga",
                      end_progress = 100,
                      start_date = (today).date(),
                      end_date = (today + pd.Timedelta("100D")).date(),
                      today = 1,
            week= 1,
            month =  1,
            quarter = 1,
            year = 1,
            historical = 1))

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
        groups = []
        progress = []
        progress_params = []
        goals_list = []
        active_goals = []
        
        test_connectivity1(self)
        create_check_group(self, groups, ["Projects", "Reading"])
        test_connectivity2(self)
        
        
        response = self.app.get('Create/Progress', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        create_check_progress(self, progress, progress_params, [["Read Book 1", "Progress", 1, 0],
                                                                ["Read Book 2", "Progress", 1, 20]])
        check_goals_page_widgets(self, progress, groups)
        
        create_goal(self, goals_to_add[0], goals_list, active_goals)
        create_goal(self, goals_to_add[1], goals_list, active_goals)
        
        check_view_goals_page_widgets(self, goals_list)
        
        create_check_group(self, groups, ["Exercise"])
        create_check_progress(self, progress, progress_params, [["Practice Yoga", "Add", 60, 0]])
        check_goals_page_widgets(self, progress, groups)
        create_goal(self, goals_to_add[2], goals_list, active_goals)
        check_view_goals_page_widgets(self, active_goals)
        
if __name__ == "__main__":
    unittest.main()
    