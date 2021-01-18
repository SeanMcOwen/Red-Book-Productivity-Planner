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



class BasicTests(unittest.TestCase):
 
    ############################
    #### setup and teardown ####
    ############################
 
    # executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['DB_NAME'] = "Test.db"
        self.app = app.test_client()
        
        
    #Add in a way to copy over and save the excel files so they aren't overwritten
 
    # executed after each test
    def tearDown(self):
        pass
    
    def test_main_page(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        response = self.app.post(
          '/Create/Group',
          data = dict(group_name="Projects"),
          follow_redirects=True
          )
        
        
if __name__ == "__main__":
    unittest.main()
    