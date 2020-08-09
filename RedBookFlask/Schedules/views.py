from flask import Blueprint,render_template,redirect,url_for
from bokeh.embed import server_document
import sqlite3
import RedBook

database_name = 'Goals.db'


schedules_blueprint = Blueprint('schedules',
                              __name__,
                              template_folder='templates')





@schedules_blueprint.route("/Schedules")
def schedules_page():
    script = server_document('http://localhost:5006/schedules')
    return render_template("embed.html", script=script, template="Flask")





   
@schedules_blueprint.route("/EffectiveDates")
def effective_dates_page():
    with sqlite3.connect(database_name) as conn:
        goals, work_log = RedBook.Data.process_goals_SQL(conn)
        goals = goals[goals['Group'] != 'Fitness']
    effective_dates_table = RedBook.Tables.build_effective_date_table(goals)
    tables = ""
    tables += "<h3>Effective Dates</h3>"
    tables += effective_dates_table.to_html()
    tables += "<br>"
    return tables

@schedules_blueprint.route("/SchedulesPIT")
def schedules_PIT_page():
    script = server_document('http://localhost:5006/schedulesPIT')
    return render_template("embed.html", script=script, template="Flask")


@schedules_blueprint.route("/calendar")
def calendar_page():
    script = server_document('http://localhost:5006/calendar')
    return render_template("embed.html", script=script, template="Flask")