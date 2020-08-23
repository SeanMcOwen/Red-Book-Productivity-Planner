from flask import Flask,request, render_template
import sqlite3
import pandas as pd
from Create_Databases import excel_to_db
import RedBook, RedBookBokeh

from threading import Thread
from tornado.ioloop import IOLoop
from bokeh.embed import server_document

from bokeh.server.server import Server
import os

database_name = 'Goals.db'
"""if 'Goals.csv' not in os.listdir('/'):
    cols = ['Goal #', 'Goal Name', 'Group', 'Start Progress', 'Goal Progress',
       'Start Date', 'End Date', 'Progress Type', 'Completed', 'Units',
       'Today', 'Week', 'Month', 'Quarter', 'Year', 'Historical']
    pd.DataFrame([], columns=cols).to_csv("Goals.csv")"""
with sqlite3.connect(database_name) as conn:
    excel_to_db(conn)
app = Flask(__name__)


from RedBookFlask.Schedules.views import schedules_blueprint
from RedBookFlask.Increments.views import increments_blueprint
from RedBookFlask.Goals.views import goals_blueprint
from RedBookFlask.Groups.views import groups_blueprint
from RedBookFlask.Create.views import create_blueprint

app.register_blueprint(schedules_blueprint,url_prefix="/Schedules")
app.register_blueprint(increments_blueprint,url_prefix="/Increments")
app.register_blueprint(goals_blueprint,url_prefix="/Goals")
app.register_blueprint(groups_blueprint,url_prefix="/Groups")
app.register_blueprint(create_blueprint,url_prefix="/Create")

app.config['SECRET_KEY'] = 'TEST'


@app.route("/",methods=['GET', 'POST'])
def main():
    return render_template("Home.html", template="Flask")

