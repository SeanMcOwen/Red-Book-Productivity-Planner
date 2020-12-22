from flask import Blueprint,render_template,redirect,url_for
from bokeh.embed import server_document
import sqlite3
import RedBook

database_name = 'Goals.db'


rules_blueprint = Blueprint('rules',
                              __name__,
                              template_folder='templates')





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

    return render_template("CreateGoals.html", template="Flask")


