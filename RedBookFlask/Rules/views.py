from flask import Blueprint,render_template,redirect,url_for, flash
from bokeh.embed import server_document
import sqlite3
import RedBook
from flask_wtf import FlaskForm
from wtforms import (StringField, BooleanField,
                     RadioField,SelectField,TextField,
                     TextAreaField,SubmitField, FloatField, IntegerField)
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, NoneOf
import pandas as pd
import numpy as np

database_name = 'Goals.db'


rules_blueprint = Blueprint('rules',
                              __name__,
                              template_folder='templates')


def write_rule(rules):
    with sqlite3.connect(database_name) as conn:
        rules.to_sql("rules", conn, if_exists='append', index=False)
        df = pd.read_sql("SELECT * FROM rules", conn)
        df.to_csv("Rules.csv", index=False)

def flash_errors(form):
    """Flashes form errors"""
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ), 'error')

@rules_blueprint.route("/CreateGoal",methods=['GET', 'POST'])
def create_goal_rule_page():
    try:
        with sqlite3.connect(database_name) as conn:
            goals, work_log = RedBook.Data.process_goals_SQL(conn)
            expected_progress_table, expected_work_table, percent_left_table, expected_work_tables = RedBook.Tables.build_expected_work_tables(goals)
            expected_progress_table_today = RedBook.Tables.build_expected_work_tables_today(goals)
    except:
        error = "<h3>Please create a goal first.</h3>"
        return render_template("ErrorPage.html", error=error,
                                   template="Flask")
    
    
    
    forms = {"MED": GoalMEDForm(),
             "ED": GoalEDForm(),
             "GICT":GoalIncrementCompletedToday(),
             "GIC": GoalIncrementCompleted()}
    
    
    if forms["MED"].submit1.data:
        if forms["MED"].validate_on_submit():
            form = forms["MED"]
            data = {"Rule Name": form.rule_name.data,
                "N Days": form.number_days.data,
                "Rule Type": "MED",
                "Schedule": np.NaN
                }
            data = pd.Series(data).to_frame().T
            write_rule(data)
        else:
            flash_errors(forms["MED"])
    
    if forms["ED"].submit2.data:
        if forms["ED"].validate_on_submit():
            form = forms["ED"]
            data = {"Rule Name": form.rule_name.data,
                "N Days": form.number_days.data,
                "Rule Type": "ED",
                "Schedule": form.schedule.data
                }
            data = pd.Series(data).to_frame().T
            write_rule(data)
        else:
            flash_errors(forms["ED"])
            
    if forms["GICT"].submit3.data:
        if forms["GICT"].validate_on_submit():
            form = forms["GICT"]
            data = {"Rule Name": form.rule_name.data,
                "N Days": np.NaN,
                "Rule Type": "GICT",
                "Schedule": form.schedule.data
                }
            data = pd.Series(data).to_frame().T
            write_rule(data)
        else:
            flash_errors(forms["GICT"])
            
    if forms["GIC"].submit4.data:
        if forms["GIC"].validate_on_submit():
            form = forms["GIC"]
            data = {"Rule Name": form.rule_name.data,
                "N Days": np.NaN,
                "Rule Type": "GIC",
                "Schedule": form.schedule.data
                }
            data = pd.Series(data).to_frame().T
            write_rule(data)
        else:
            flash_errors(forms["GIC"])
            
    return render_template("CreateGoals.html",forms=forms, template="Flask")

def update_choices():
    with sqlite3.connect(database_name) as conn:
        rule_names = list(pd.read_sql("SELECT * FROM rules", con=conn)['Rule Name'].values)
        return rule_names

    

class GoalMEDForm(FlaskForm):
    try:
        with sqlite3.connect(database_name) as conn:
            rule_names = list(pd.read_sql("SELECT * FROM rules", con=conn)['Rule Name'].values)
    except:
        rule_names = []
    number_days = IntegerField('Number of Days', validators=[DataRequired()])
    rule_name = StringField('Rule Name', validators=[DataRequired(), NoneOf(rule_names)])
    submit1 = SubmitField('Submit')
    
class GoalEDForm(FlaskForm):
    try:
        with sqlite3.connect(database_name) as conn:
            rule_names = list(pd.read_sql("SELECT * FROM rules", con=conn)['Rule Name'].values)
    except:
        rule_names = []
    number_days = IntegerField('Number of Days', validators=[DataRequired()])
    rule_name = StringField('Rule Name', validators=[DataRequired(), NoneOf(rule_names)])
    submit2 = SubmitField('Submit')
    number_days = IntegerField('Number of Days', validators=[DataRequired()])    
    schedule = SelectField('Schedule', choices=[(x, x) for x in ['Historical', 'Today', 'Week', 'Month', 'Quarter', 'Year']])
    
class GoalIncrementCompletedToday(FlaskForm):
    try:
        with sqlite3.connect(database_name) as conn:
            rule_names = list(pd.read_sql("SELECT * FROM rules", con=conn)['Rule Name'].values)
    except:
        rule_names = []
    schedule = SelectField('Schedule', choices=[(x, x) for x in ['Historical', 'Today', 'Week', 'Month', 'Quarter', 'Year']])
    rule_name = StringField('Rule Name', validators=[DataRequired(), NoneOf(rule_names)])
    submit3 = SubmitField('Submit')


class GoalIncrementCompleted(FlaskForm):
    try:
        with sqlite3.connect(database_name) as conn:
            rule_names = list(pd.read_sql("SELECT * FROM rules", con=conn)['Rule Name'].values)
    except:
        rule_names = []
    schedule = SelectField('Schedule', choices=[(x, x) for x in ['Historical', 'Today', 'Week', 'Month', 'Quarter', 'Year']])
    rule_name = StringField('Rule Name', validators=[DataRequired(), NoneOf(rule_names)])
    submit4 = SubmitField('Submit')



    