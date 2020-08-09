from flask import Blueprint,render_template,redirect,url_for
from bokeh.embed import server_document
import sqlite3
import RedBook

database_name = 'Goals.db'


groups_blueprint = Blueprint('groups',
                              __name__,
                              template_folder='templates')





@groups_blueprint.route("/CalendarProgress")
def calendar_progress_page():
    script = server_document('http://localhost:5006/GroupCalendarProgress')
    return render_template("embed.html", script=script, template="Flask")