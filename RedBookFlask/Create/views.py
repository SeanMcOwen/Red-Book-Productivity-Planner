from flask import Blueprint,render_template,redirect,url_for, request, redirect, flash
from bokeh.embed import server_document
import sqlite3
from flask_wtf import FlaskForm
from wtforms import (StringField, BooleanField,
                     RadioField,SelectField,TextField,
                     TextAreaField,SubmitField, FloatField)
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired
import RedBook
import pandas as pd
import os
from datetime import datetime
import numpy as np

database_name = 'Goals.db'


create_blueprint = Blueprint('create',
                              __name__,
                              template_folder='templates')


def flash_errors(form):
    """Flashes form errors"""
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ), 'error')

def form_to_pandas(form):
    data = {"Goal Name": form.goal_name.data,
            "Start Progress": form.start_progress.data,
            "Goal Progress": form.end_progress.data,
            "Start Date": pd.to_datetime(form.start_date.data),
            "End Date": pd.to_datetime(form.end_date.data),
            "Progress Type": form.progress_type.data,
            "Completed": "",
            "Units": form.units.data,
            "Today": form.today.data,
            "Week": form.week.data,
            "Month": form.month.data,
            "Quarter": form.quarter.data,
            "Year": form.year.data,
            "Historical": form.historical.data
            }
    if form.existing_bool.data:
        data['Group'] = form.group_name_select.data
    else:
        data['Group'] = form.group_name.data
    if form.existing_bool2.data:
        data['Progress Name'] = form.progress_name_select.data
    else:
        data['Progress Name'] = form.progress_name.data
    data['Goal #'] = -1
    
    data = pd.Series(data)
    return data

@create_blueprint.route("/Goals",methods=['GET', 'POST'])
def goals_page():
    form = GoalForm()
    form.group_name_select.choices, form.progress_name_select.choices = update_choices()
    if form.validate_on_submit():
        goals = form_to_pandas(form).to_frame().transpose()

        progress_name = goals['Progress Name'].iloc[0]
        with sqlite3.connect(database_name) as conn:
            goals.to_sql("goals", conn, if_exists='append', index=False)
            df = pd.read_sql("SELECT * FROM goals", conn)
            df['Start Date'] = pd.to_datetime(df['Start Date'])
            df['End Date'] = pd.to_datetime(df['End Date'])
            df.to_csv("Goals.csv", index=False)
            
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            tables = [x[0] for x in tables]
            
            if "progress" in tables:
                df = pd.read_sql("SELECT * FROM progress", conn)
                if progress_name in df['Goal Name'].values:
                    pass
                else:
                    progress_type = goals['Progress Type'].iloc[0]
                    if progress_type == "Add":
                        value = 0
                    elif progress_type == 'Progress':
                        value = goals['Start Progress']
                    else:
                        assert False
                    add_on = pd.Series([pd.to_datetime(datetime.now().date()),
                                     progress_name,
                                     value
                                     ], index=['Date', 'Goal Name', 'Value']).to_frame().transpose()
                    add_on.to_sql("progress", conn, if_exists='append', index=False)
            else:
                progress_type = goals['Progress Type'].iloc[0]
                if progress_type == "Add":
                    value = 0
                elif progress_type == 'Progress':
                    value = goals['Start Progress']
                else:
                    assert False
                add_on = pd.Series([pd.to_datetime(datetime.now().date()),
                                     progress_name,
                                     value
                                     ], index=['Date', 'Goal Name', 'Value']).to_frame().transpose()
                add_on.to_sql("progress", conn, if_exists='append', index=False)
            df = pd.read_sql("SELECT * FROM progress", conn).pivot("Date", "Goal Name", "Value")
            df.to_csv("project_log.csv")
        #form.update_choices()
        #form = GoalForm()
        form.group_name_select.choices, form.progress_name_select.choices = update_choices()
        return render_template("Create/Goals.html", form=form, template="Flask")
    else:
        flash_errors(form)
    #form.update_choices()
    return render_template("Create/Goals.html", form=form, template="Flask")


@create_blueprint.route("/Group",methods=['GET', 'POST'])
def group_page():
    form = GroupForm()
    if form.validate_on_submit():
        group_name = form.group_name.data
        current_date = datetime.now()
        group_data = pd.DataFrame([[group_name, current_date]],
                     columns = ['Group', 'Creation Date'])
        with sqlite3.connect(database_name) as conn:
            try:
                temp = pd.read_sql("SELECT * FROM groups", conn)['Group'].values
            except:
                temp = []
            if group_data['Group'].iloc[0] not in temp:
                group_data.to_sql("groups", conn, if_exists='append', index=False)
                group_data = pd.read_sql("SELECT * FROM groups", conn)
                group_data.to_csv("Group.csv")
        render_template("Create/Group.html", cur_groups=temp, form=form,template="Flask")
    try:
        with sqlite3.connect(database_name) as conn:
            temp = pd.read_sql("SELECT * FROM groups", conn)['Group'].values
    except:
        temp = []
    return render_template("Create/Group.html", form=form, cur_groups=temp,template="Flask")

@create_blueprint.route("/Progress",methods=['GET', 'POST'])
def progress_page():
    form = ProgressForm()
    if form.validate_on_submit():
        
        #ADD A CHECK TO MAKE SURE IT IS NOT ALREADY IN THERE
        
        group_name = form.group_name.data
        current_date = datetime.now()
        group_data = pd.DataFrame([[group_name, current_date]],
                     columns = ['Group', 'Creation Date'])
        with sqlite3.connect(database_name) as conn:
            try:
                temp = pd.read_sql("SELECT * FROM groups", conn)['Group'].values
            except:
                temp = []
            if group_data['Group'].iloc[0] not in temp:
                group_data.to_sql("groups", conn, if_exists='append', index=False)
                group_data = pd.read_sql("SELECT * FROM groups", conn)
                group_data.to_csv("Group.csv")
        render_template("Create/Group.html", cur_groups=temp, form=form,template="Flask")
    #try:
    #    with sqlite3.connect(database_name) as conn:
    #        temp = pd.read_sql("SELECT * FROM groups", conn)['Group'].values
    #except:
    #    temp = []
    return render_template("Create/Progress.html", form=form, template="Flask")


@create_blueprint.route("/Update Progress",methods=['GET', 'POST'])
def update_progress_page():
    with sqlite3.connect(database_name) as conn:
        goals, work_log = RedBook.Data.process_goals_SQL(conn)
    if request.method == 'POST':
        goal_name  = request.values.get('goal')
        update_val  = request.values.get('update_val')
        update_date  = request.values.get('date')
        if update_val is None:
            work_log = pd.read_sql("SELECT * FROM progress WHERE `Goal Name` = '{}'".format(goal_name), conn).pivot("Date", "Goal Name", "Value")
            work_log.index = pd.to_datetime(work_log.index)
            work_log = work_log.reindex(index=pd.date_range(work_log.index[0], pd.to_datetime(datetime.now().date()))).sort_index(ascending=False)
            work_log = work_log.fillna("")
            work_log.index = [x.strftime("%m/%d/%Y") for x in work_log.index]
            work_log = work_log.reset_index().values
            work_log = [list(x) for x in work_log]
            
            goals_l = list(goals['Progress Name'].unique())
            goals_l = [goal_name] + [x for x in goals_l if x != goal_name]
    
            return render_template("Create/Update Progress.html", goals=goals_l, work_log=work_log, goal=goal_name, template="Flask")
        else:
            
            update_date = pd.to_datetime(datetime.strptime(update_date, "%m/%d/%Y"))
            
            
            
            c = conn.cursor()
            c.execute('''DELETE FROM progress WHERE `Goal Name` = '{}' AND Date = datetime('{}')'''.format(goal_name, update_date.strftime('%Y-%m-%d %H:%M:%S')))
            conn.commit()
            
            if update_val == "":
                #Just delete if exists
                pass
            else:
                upload = pd.Series([update_val, update_date, goal_name], index=['Value', 'Date', 'Goal Name'])
                upload = upload.to_frame().transpose()
                upload.to_sql("progress", conn, if_exists='append', index=False)
                
            work_log = pd.read_sql("SELECT * FROM progress", conn).pivot("Date", "Goal Name", "Value")
            work_log.to_csv("project_log.csv")
            
            work_log = pd.read_sql("SELECT * FROM progress WHERE `Goal Name` = '{}'".format(goal_name), conn).pivot("Date", "Goal Name", "Value")
            work_log.index = pd.to_datetime(work_log.index)
            work_log = work_log.reindex(index=pd.date_range(work_log.index[0], pd.to_datetime(datetime.now().date()))).sort_index(ascending=False)
            work_log = work_log.fillna("")
            work_log.index = [x.strftime("%m/%d/%Y") for x in work_log.index]
            work_log = work_log.reset_index().values
            work_log = [list(x) for x in work_log]
            
            goals_l = list(goals['Progress Name'].unique())
            goals_l = [goal_name] + [x for x in goals_l if x != goal_name]
            
    
            return render_template("Create/Update Progress.html", goals=goals_l, work_log=work_log, goal=goal_name, template="Flask")
    return render_template("Create/Update Progress.html", goals=list(goals['Progress Name'].unique()), template="Flask")


def update_choices():
    if True:
        if "Goals.db" in os.listdir("."):
            with sqlite3.connect(database_name) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                tables = [x[0] for x in tables]
                if len(tables) == 0:
                    existing_groups = ['General']
                    existing_progress = ['General']
                else:
                    goals, work_log = RedBook.Data.process_goals_SQL(conn)
                    existing_groups = goals['Group'].unique()
                    existing_progress =goals['Progress Name'].unique()
                
        else:
            existing_groups = ['General']
            existing_progress = ['General']
            
        return [(x, x) for x in existing_groups], [(x, x) for x in existing_progress]
class GoalForm(FlaskForm):

    if "Goals.db" in os.listdir("."):
        with sqlite3.connect(database_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            tables = [x[0] for x in tables]
            if 'goals' not in tables:
                existing_groups = ['General']
                existing_progress = ['General']
            else:
                goals, work_log = RedBook.Data.process_goals_SQL(conn)
                existing_groups = goals['Group'].unique()
                existing_progress =goals['Progress Name'].unique()
            
    else:
        existing_groups = ['General']
        existing_progress = ['General']
    goal_name = StringField('Goal Name', validators=[DataRequired()])
    existing_bool = BooleanField('Use Existing Group Field', default=True)
    existing_bool2 = BooleanField('Use Existing Progress Field', default=False)
    group_name_select = SelectField('Group Name (Existing)', coerce=str)
    #group_name_select = SelectField('Group Name (Existing)')
    group_name = StringField('Group Name (New)', default='General')
    progress_name_select = SelectField('Progress Name', coerce=str)
    #progress_name_select = SelectField('Progress Name')
    progress_name = StringField('Progress Name (New)', default='Goal')
    start_progress = FloatField("Start Progress")
    end_progress = FloatField("End Progress")
    start_date = DateField("Start Date")
    end_date = DateField("End Date")
    progress_type = SelectField('Progress Type', choices=[(x, x) for x in ["Add", "Progress"]])
    units = FloatField("Units", default=1)
    today = BooleanField('Today', default=True)
    week = BooleanField('Week', default=True)
    month = BooleanField('Month', default=True)
    quarter = BooleanField('Quarter', default=True)
    year = BooleanField('Year', default=True)
    historical = BooleanField("Historical", default=True)
    submit = SubmitField('Submit')


class GroupForm(FlaskForm):
    group_name = StringField('Group Name', validators=[DataRequired()])
    submit = SubmitField('Create Group')


class ProgressForm(FlaskForm):
    group_name = StringField('Progress Name', validators=[DataRequired()])
    progress_type = SelectField('Progress Type', choices=[(x, x) for x in ["Add", "Progress"]])
    units = FloatField("Units", default=1)
    submit = SubmitField('Create Progress')