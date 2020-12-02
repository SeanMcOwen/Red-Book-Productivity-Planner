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
    with sqlite3.connect(database_name) as conn:
        if not RedBook.Data.check_table_exists(conn, 'habits'):
            error = "<h3>Please create a habit.</h3>"
            return render_template("ErrorPage.html", error=error,
                                   template="Flask")
        habits, progress = RedBook.Data.process_habits_SQL(conn)
    tables = RedBook.Tables.create_streak_tables(habits)
    
    tables_html = ""
    for key in tables.keys():
        tables_html += "<h3>{}</h3><br>".format(key)
        tables_html += tables[key].to_html(index=False)
        tables_html+="<br><br>"
        
    return render_template("Streaks.html", tables=tables_html, template="Flask")

@habits_blueprint.route("/Habits",methods=['GET', 'POST'])
def habits_page():
    with sqlite3.connect(database_name) as conn:
        if not RedBook.Data.check_table_exists(conn, 'habits'):
            error = "<h3>Please create a habit.</h3>"
            return render_template("ErrorPage.html", error=error,
                                   template="Flask")
        habits, progress = RedBook.Data.process_habits_SQL(conn)
        
    if request.method == 'POST':
        habit_name  = request.values.get('habit')
        habit_names = list(habits['Habit Name'].values)
        habit_names.pop(habit_names.index(habit_name))
        habit_names = [habit_name] + habit_names
        
        temp = habits.set_index('Habit Name').loc[habit_name]
        habit_data = {}
        habit_data = {"Habit Name": habit_name,
                      "Frequency": temp['Frequency'],
                      "Group": temp['Group'],
                      "Start Date": temp['Start Date'],
                      "Units": temp['Units'],
                      "Streak": temp['Object'].streak}
        
        return render_template("Habits.html", habits=habit_names,habit_data=habit_data,template="Flask")

        
    
    return render_template("Habits.html", habits=list(habits['Habit Name'].values),template="Flask")



