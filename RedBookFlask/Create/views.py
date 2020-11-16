from flask import Blueprint,render_template,redirect,url_for, request, redirect, flash
from bokeh.embed import server_document
import sqlite3
from flask_wtf import FlaskForm
from wtforms import (StringField, BooleanField,
                     RadioField,SelectField,TextField,
                     TextAreaField,SubmitField, FloatField, IntegerField)
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, NoneOf
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
            "Goal Progress": form.end_progress.data,
            "Start Date": pd.to_datetime(form.start_date.data),
            "End Date": pd.to_datetime(form.end_date.data),
            "Completed": "",
            "Today": form.today.data,
            "Week": form.week.data,
            "Month": form.month.data,
            "Quarter": form.quarter.data,
            "Year": form.year.data,
            "Historical": form.historical.data
            }
    data['Group'] = form.group_name_select.data
    data['Progress Name'] = form.progress_name_select.data

    data['Goal #'] = -1
    

    
    data = pd.Series(data)
    return data


def form_to_pandas_habits(form):
    data = {"Habit Name": form.habit_name.data,
            "Group": form.group_name_select.data,
            "Start Date": pd.to_datetime(form.start_date.data),
            "Completed": "",
            "Units": form.units.data,
            "Frequency": form.frequency.data
            }
    data = pd.Series(data)

    return data

def form_to_pandas_tasks(form):
    data = {"Task Name": form.task_name.data,
            "Group": form.group_name_select.data,
            "Due Date": pd.to_datetime(form.due_date.data),
            "Completed": ""
            }
    data = pd.Series(data)

    return data

def create_bulk_tasks(first_due_date, time_between, prefix, start, end, group):
    tasks = [[prefix + " "+ str(x),
              group,
              first_due_date + pd.Timedelta("{}D".format((x-1)* time_between)),
              ""] for x in range(start, end+1)]
    tasks = pd.DataFrame(tasks, columns=['Task Name', 'Group', 'Due Date', 'Completed'])
    return tasks

def form_to_pandas_tasks_bulk(form):
    data = {"Task Name": form.task_name.data,
            "Group": form.group_name_select.data,
            "Due Date": pd.to_datetime(form.due_date.data),
            "Start": form.start.data,
            "End": form.end.data,
            "Days Between": form.days_between.data,
            
            }
    data = create_bulk_tasks(data['Due Date'], data['Days Between'], data['Task Name'],
                             data['Start'], data['End'], data['Group'])
    
    

    return data



@create_blueprint.route("/Goals",methods=['GET', 'POST'])
def goals_page():
    with sqlite3.connect(database_name) as conn:
        if not RedBook.Data.check_table_exists(conn, 'groups'):
            error = "<h3>Please create a group before creating goals.</h3>"
            return render_template("ErrorPage.html", error=error,
                                   template="Flask")
        if not RedBook.Data.check_table_exists(conn, 'progress'):
            error = "<h3>Please create a progress object before creating goals.</h3>"
            return render_template("ErrorPage.html", error=error,
                                   template="Flask")
    form = GoalForm()
    form.group_name_select.choices, form.progress_name_select.choices = update_choices()
    if form.validate_on_submit():
        goals = form_to_pandas(form).to_frame().transpose()

        with sqlite3.connect(database_name) as conn:
            goals.to_sql("goals", conn, if_exists='append', index=False)
            df = pd.read_sql("SELECT * FROM goals", conn)
            df['Start Date'] = pd.to_datetime(df['Start Date'])
            df['End Date'] = pd.to_datetime(df['End Date'])
            df.to_csv("Goals.csv", index=False)
            

            

        #form.update_choices()
        #form = GoalForm()
        form.group_name_select.choices, form.progress_name_select.choices = update_choices()
        return render_template("Create/Goals.html", form=form, template="Flask")
    else:
        flash_errors(form)
    #form.update_choices()
    return render_template("Create/Goals.html", form=form, template="Flask")

@create_blueprint.route("/Task",methods=['GET', 'POST'])
def task_page():
    with sqlite3.connect(database_name) as conn:
        if not RedBook.Data.check_table_exists(conn, 'groups'):
            error = "<h3>Please create a group before creating tasks.</h3>"
            return render_template("ErrorPage.html", error=error,
                                   template="Flask")
    form = TaskForm()
    form.group_name_select.choices = update_choices()[0]
    if form.validate_on_submit():
        tasks = form_to_pandas_tasks(form).to_frame().transpose()
        with sqlite3.connect(database_name) as conn:
            tasks.to_sql("tasks", conn, if_exists='append', index=False)
            df = pd.read_sql("SELECT * FROM tasks", conn)
            df['Due Date'] = pd.to_datetime(df['Due Date'])
            df.to_csv("Tasks.csv", index=False)
            

            

        form.group_name_select.choices = update_choices()[0]
        return render_template("Create/Task.html", form=form, template="Flask")
    else:
        flash_errors(form)
        

    return render_template("Create/Task.html", form=form, template="Flask")

@create_blueprint.route("/Bulk Tasks",methods=['GET', 'POST'])
def bulk_task_page():
    with sqlite3.connect(database_name) as conn:
        if not RedBook.Data.check_table_exists(conn, 'groups'):
            error = "<h3>Please create a group before creating tasks.</h3>"
            return render_template("ErrorPage.html", error=error,
                                   template="Flask")
    form = BulkTaskForm()
    form.group_name_select.choices = update_choices()[0]
    if form.validate_on_submit():
        tasks = form_to_pandas_tasks_bulk(form)
        
        with sqlite3.connect(database_name) as conn:
            tasks.to_sql("tasks", conn, if_exists='append', index=False)
            df = pd.read_sql("SELECT * FROM tasks", conn)
            df['Due Date'] = pd.to_datetime(df['Due Date'])
            df.to_csv("Tasks.csv", index=False)
            

            

        form.group_name_select.choices = update_choices()[0]
        return render_template("Create/BulkTask.html", form=form, template="Flask")
    else:
        flash_errors(form)
        

    return render_template("Create/BulkTask.html", form=form, template="Flask")


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
        

        progress_name = form.progress_name.data
        progress_type = form.progress_type.data
        units = form.units.data
        starting_value = form.starting_value.data
        add = pd.Series([pd.to_datetime((datetime.now() - pd.Timedelta("1D")).date()),
                                     progress_name,
                                     starting_value
                                     ], index=['Date', 'Goal Name', 'Value']).to_frame().transpose()
        add2 = pd.Series([progress_name,
                                     units, progress_type
                                     ], index=['Goal Name', 'Units', 'Progress Type']).to_frame().transpose()
        with sqlite3.connect(database_name) as conn:
            add.to_sql("progress", conn, if_exists='append', index=False)
            df = pd.read_sql("SELECT * FROM progress", conn).pivot("Date", "Goal Name", "Value")
            df.to_csv("project_log.csv")
            add2.to_sql("progress_params", conn, if_exists='append', index=False)
            df = pd.read_sql("SELECT * FROM progress_params", conn)
            df.to_csv("progress_params.csv")
        form = ProgressForm()
        render_template("Create/Progress.html", form=form, template="Flask")
    else:
        flash_errors(form)
    #try:
    #    with sqlite3.connect(database_name) as conn:
    #        temp = pd.read_sql("SELECT * FROM groups", conn)['Group'].values
    #except:
    #    temp = []
    return render_template("Create/Progress.html", form=form, template="Flask")


@create_blueprint.route("/Update Progress",methods=['GET', 'POST'])
def update_progress_page():
    with sqlite3.connect(database_name) as conn:
        if not RedBook.Data.check_table_exists(conn, 'progress'):
            error = "<h3>Please create a progress task.</h3>"
            return render_template("ErrorPage.html", error=error,
                                   template="Flask")
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
            
            goals1, work_log1 = RedBook.Data.process_goals_SQL(conn)
            RedBook.Data.check_goal_completion(conn, goals1)
    
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
            
            goals1, work_log1 = RedBook.Data.process_goals_SQL(conn)
            RedBook.Data.check_goal_completion(conn, goals1)
            return render_template("Create/Update Progress.html", goals=goals_l, work_log=work_log, goal=goal_name, template="Flask")
    return render_template("Create/Update Progress.html", goals=list(goals['Progress Name'].unique()), template="Flask")

@create_blueprint.route("/Update Tasks",methods=['GET', 'POST'])
def update_tasks_page():
    with sqlite3.connect(database_name) as conn:
        if not RedBook.Data.check_table_exists(conn, 'tasks'):
            error = "<h3>Please create a task.</h3>"
            return render_template("ErrorPage.html", error=error,
                                   template="Flask")
    with sqlite3.connect(database_name) as conn:
        tasks = RedBook.Data.pull_tasks_SQL(conn)
    if request.method == 'POST':
        task  = request.values.get('task')
        
        with sqlite3.connect(database_name) as conn:
            conn.cursor().execute("UPDATE tasks SET Completed = 'Completed' WHERE `Task Name` = '{}'".format(task))
            conn.commit()
            df = pd.read_sql("SELECT * FROM tasks", conn)
            df['Due Date'] = pd.to_datetime(df['Due Date'])
            df.to_csv("Tasks.csv", index=False)

            tasks = RedBook.Data.pull_tasks_SQL(conn)
            
            completed = pd.DataFrame([[task, "Task", pd.to_datetime(datetime.today().date())]],
                                 columns = ['Name', 'Type', 'Date'])
            completed.to_sql("Completed", conn, if_exists='append', index=False)
            df = pd.read_sql("SELECT * FROM Completed", conn)
            df['Date'] = pd.to_datetime(df['Date'])
            df.to_csv("Completed.csv", index=False)
        
        return render_template("Create/Update Tasks.html", tasks=tasks.to_dict(orient='records'), template="Flask")

    return render_template("Create/Update Tasks.html", tasks=tasks.to_dict(orient='records'), template="Flask")



@create_blueprint.route("/Update Habits",methods=['GET', 'POST'])
def update_habits_page():
    with sqlite3.connect(database_name) as conn:
        if not RedBook.Data.check_table_exists(conn, 'habits'):
            error = "<h3>Please create a habit.</h3>"
            return render_template("ErrorPage.html", error=error,
                                   template="Flask")
    with sqlite3.connect(database_name) as conn:
        habits, work_log = RedBook.Data.process_habits_SQL(conn)
    if request.method == 'POST':
        habit_name  = request.values.get('habit')
        update_val  = request.values.get('update_val')
        update_date  = request.values.get('date')
        if update_val is None:
            work_log = pd.read_sql("SELECT * FROM habits_progress WHERE `Habit Name` = '{}'".format(habit_name), conn).pivot("Date", "Habit Name", "Progress")
            work_log.index = pd.to_datetime(work_log.index)
            work_log = work_log.reindex(index=pd.date_range(work_log.index[0], pd.to_datetime(datetime.now().date()))).sort_index(ascending=False)
            work_log = work_log.fillna("")
            work_log.index = [x.strftime("%m/%d/%Y") for x in work_log.index]
            work_log = work_log.reset_index().values
            work_log = [list(x) for x in work_log]
            
            habits_l = list(habits['Habit Name'].unique())
            habits_l = [habit_name] + [x for x in habits_l if x != habit_name]
    
            return render_template("Create/Update Habits.html", habits=habits_l, work_log=work_log, habit=habit_name, template="Flask")
        else:
            
            update_date = pd.to_datetime(datetime.strptime(update_date, "%m/%d/%Y"))
            
            

            c = conn.cursor()
            c.execute('''DELETE FROM habits_progress WHERE `Habit Name` = '{}' AND Date = datetime('{}')'''.format(habit_name, update_date.strftime('%Y-%m-%d %H:%M:%S')))
            conn.commit()
            
            if update_val == "":
                #Just delete if exists
                pass
            else:
                upload = pd.Series([update_val, update_date, habit_name], index=['Progress', 'Date', 'Habit Name'])
                upload = upload.to_frame().transpose()
                upload.to_sql("habits_progress", conn, if_exists='append', index=False)
                
            work_log = pd.read_sql("SELECT * FROM habits_progress", conn)
            work_log.to_csv("Habits Progress.csv")
            
            work_log = pd.read_sql("SELECT * FROM habits_progress WHERE `Habit Name` = '{}'".format(habit_name), conn).pivot("Date", "Habit Name", "Progress")
            work_log.index = pd.to_datetime(work_log.index)
            work_log = work_log.reindex(index=pd.date_range(work_log.index[0], pd.to_datetime(datetime.now().date()))).sort_index(ascending=False)
            work_log = work_log.fillna("")
            work_log.index = [x.strftime("%m/%d/%Y") for x in work_log.index]
            work_log = work_log.reset_index().values
            work_log = [list(x) for x in work_log]
            
            habits_l = list(habits['Habit Name'].unique())
            habits_l = [habit_name] + [x for x in habits_l if x != habit_name]
            
    
            return render_template("Create/Update Habits.html", habits=habits_l, work_log=work_log, habit=habit_name, template="Flask")
    return render_template("Create/Update Habits.html", habits=list(habits['Habit Name'].unique()), template="Flask")

@create_blueprint.route("/Habits",methods=['GET', 'POST'])
def habits_page():
    with sqlite3.connect(database_name) as conn:
        if not RedBook.Data.check_table_exists(conn, 'groups'):
            error = "<h3>Please create a group before creating habits.</h3>"
            return render_template("ErrorPage.html", error=error,
                                   template="Flask")
    form = HabitsForm()
    form.group_name_select.choices = update_choices()[0]
    if form.validate_on_submit():
        habits = form_to_pandas_habits(form).to_frame().transpose()

        with sqlite3.connect(database_name) as conn:
            habits.to_sql("habits", conn, if_exists='append', index=False)
            df = pd.read_sql("SELECT * FROM habits", conn)
            df['Start Date'] = pd.to_datetime(df['Start Date'])
            df.to_csv("Habits.csv")
            habit_name = habits.iloc[0]['Habit Name']
            start_date = habits.iloc[0]['Start Date']
            progress = pd.DataFrame([[habit_name, start_date, 0]],
                                    columns= ['Habit Name', 'Date', 'Progress'])
            progress.to_sql("habits_progress", conn, if_exists='append', index=False)
            progress = pd.read_sql("SELECT * FROM habits_progress", conn)
            progress['Date'] = pd.to_datetime(progress['Date'])
            progress.to_csv("Habits Progress.csv")
            

        return render_template("Create/Habits.html", form=form, template="Flask")
    else:
        flash_errors(form)
    #form.update_choices()
    return render_template("Create/Habits.html", form=form, template="Flask")

def update_choices():
    with sqlite3.connect(database_name) as conn:
        existing_groups = list(pd.read_sql("SELECT * FROM groups", conn)['Group'].values)
        try:
            existing_progress = list(pd.read_sql("SELECT * FROM progress", conn)['Goal Name'].unique())
        except:
            existing_progress = []
            
    return [(x, x) for x in existing_groups], [(x, x) for x in existing_progress]

class HabitsForm(FlaskForm):
    habit_name = StringField('Habit Name', validators=[DataRequired()])
    group_name_select = SelectField('Group Name', coerce=str)
    start_date = DateField("Start Date")
    units = IntegerField("Units", default=1)
    frequency = SelectField('Frequency', choices=[(x, x) for x in ["Daily",
                                                                   "Weekly",
                                                                   "Monthly",
                                                                   "Quarterly",
                                                                   "Yearly"]])
    
    submit = SubmitField('Submit')
    

class GoalForm(FlaskForm):
    try:
        with sqlite3.connect(database_name) as conn:
            existing_groups = list(pd.read_sql("SELECT * FROM groups", conn)['Group'].values)
            existing_progress = list(pd.read_sql("SELECT * FROM progress", conn)['Goal Name'].unique())
            existing_goals = list(pd.read_sql("SELECT * FROM goals", conn)['Goal Name'].unique())
    except:
        existing_groups = []
        existing_progress = []
        existing_goals = []
        

    
    goal_name = StringField('Goal Name', validators=[DataRequired(), NoneOf(existing_goals)])
    group_name_select = SelectField('Group Name', coerce=str)
    progress_name_select = SelectField('Progress Name', coerce=str)
    end_progress = FloatField("Goal Progress")
    start_date = DateField("Start Date")
    end_date = DateField("End Date")
    today = BooleanField('Today', default=True)
    week = BooleanField('Week', default=True)
    month = BooleanField('Month', default=True)
    quarter = BooleanField('Quarter', default=True)
    year = BooleanField('Year', default=True)
    historical = BooleanField("Historical", default=True)
    submit = SubmitField('Submit')

class TaskForm(FlaskForm):    
    task_name = StringField('Task Name', validators=[DataRequired()])
    group_name_select = SelectField('Group Name', coerce=str)
    due_date = DateField("Due Date")
    submit = SubmitField('Submit')

class BulkTaskForm(FlaskForm):    
    task_name = StringField('Task Name', validators=[DataRequired()])
    group_name_select = SelectField('Group Name', coerce=str)
    due_date = DateField("First Due Date")
    start = IntegerField("Starting Number")
    end = IntegerField("Ending Number")
    days_between = IntegerField("Days Between")
    submit = SubmitField('Submit')

class GroupForm(FlaskForm):
    group_name = StringField('Group Name', validators=[DataRequired()])
    submit = SubmitField('Create Group')


class ProgressForm(FlaskForm):
    try:
        with sqlite3.connect(database_name) as conn:
            existing_progress = list(pd.read_sql("SELECT * FROM progress", conn)['Goal Name'].unique())
    except:
        existing_progress = []
    progress_name = StringField('Progress Name', validators=[DataRequired(),  NoneOf(existing_progress)])
    progress_type = SelectField('Progress Type', choices=[(x, x) for x in ["Add", "Progress"]])
    units = FloatField("Units", default=1)
    starting_value = FloatField("Starting Value", default=0)
    submit = SubmitField('Create Progress')