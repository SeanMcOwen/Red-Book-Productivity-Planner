from flask import Blueprint,render_template,redirect,url_for
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

database_name = 'Goals.db'


rules_blueprint = Blueprint('rules',
                              __name__,
                              template_folder='templates')


def write_rule(rules):
    with sqlite3.connect(database_name) as conn:
        rules.to_sql("rules", conn, if_exists='append', index=False)
        df = pd.read_sql("SELECT * FROM rules", conn)
        df.to_csv("Rules.csv", index=False)


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
    forms = {"MED": GoalMEDForm()}
    
    
    if forms["MED"].validate_on_submit():
        form = forms["MED"]
        data = {"Rule Name": form.rule_name.data,
            "N Days": form.number_days.data,
            "Rule Type": "MED"
            }
        data = pd.Series(data).to_frame().T
        write_rule(data)
    return render_template("CreateGoals.html",forms=forms, template="Flask")


class GoalMEDForm(FlaskForm):    
    rule_name = StringField('Rule Name', validators=[DataRequired()])
    number_days = IntegerField('Number of Days', validators=[DataRequired()])
    submit = SubmitField('Submit')
    