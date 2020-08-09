from flask import Blueprint,render_template,redirect,url_for, request
from bokeh.embed import server_document
import sqlite3
import RedBook

database_name = 'Goals.db'


goals_blueprint = Blueprint('goals',
                              __name__,
                              template_folder='templates')





@goals_blueprint.route("/Goals",methods=['GET', 'POST'])
def goals_page():
    with sqlite3.connect(database_name) as conn:
        goals, work_log = RedBook.Data.process_goals_SQL(conn)
        goals = goals[goals['Group'] != 'Fitness']
    if request.method == 'POST':
        goal_name  = request.values.get('goal')
        goal_names = list(goals['Goal Name'].values)
        goal_names.pop(goal_names.index(goal_name))
        goal_names = [goal_name] + goal_names
        goals = goals.set_index('Goal Name')
        goal_data = {}
        goal_data['Goal Name'] = goal_name
        goal_data['Group'] = goals.loc[goal_name, 'Group']
        goal_data['Start Date'] = goals.loc[goal_name, 'Start Date'].strftime("%m/%d/%Y")
        goal_data['End Date'] = goals.loc[goal_name, 'End Date'].strftime("%m/%d/%Y")
        goal_data['Start Progress'] = goals.loc[goal_name, 'Start Progress']
        goal_data['Current Progress'] = goals.loc[goal_name, 'Object'].current_progress
        goal_data['Goal Progress'] = goals.loc[goal_name, 'Goal Progress']
        goal_data['Percent Complete'] = abs(goal_data['Current Progress'] - goal_data['Start Progress']) / abs(goal_data['Goal Progress'] - goal_data['Start Progress'])
        
        scheduleScript = server_document('http://localhost:5006/schedules',
                                         arguments={'goal_name': goal_name})
        
        return render_template("Goals.html",goals=goal_names, template="Flask",
                               goal_data=goal_data, scheduleScript=scheduleScript)
        
    return render_template("Goals.html",goals=list(goals['Goal Name'].values), template="Flask")

