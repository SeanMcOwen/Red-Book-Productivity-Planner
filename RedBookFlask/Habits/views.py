from flask import Blueprint,render_template,redirect,url_for, request
from bokeh.embed import server_document
import sqlite3
import RedBook
import pandas as pd

database_name = 'Goals.db'


habits_blueprint = Blueprint('habits',
                              __name__,
                              template_folder='templates')





@habits_blueprint.route("/Streaks",methods=['GET', 'POST'])
def streaks_page():
    pass

@habits_blueprint.route("/Habits",methods=['GET', 'POST'])
def habits_page():
    pass