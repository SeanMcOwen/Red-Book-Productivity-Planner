from flask import Blueprint,render_template,redirect,url_for
from bokeh.embed import server_document
import sqlite3
import RedBook

database_name = 'Goals.db'


playground_blueprint = Blueprint('playground',
                              __name__,
                              template_folder='templates')





@playground_blueprint.route("/DataTables",methods=['GET', 'POST'])
def data_tables_page():
    return render_template("DataTables.html")
