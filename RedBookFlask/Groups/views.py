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
    with sqlite3.connect(database_name) as conn:
        if not RedBook.Data.check_table_exists(conn, 'goals'):
            error = "<h3>Please create a goal first.</h3>"
            return render_template("ErrorPage.html", error=error,
                                   template="Flask")
    script = server_document('http://localhost:5006/GroupCalendarProgress')
    return render_template("embed.html", script=script, template="Flask")