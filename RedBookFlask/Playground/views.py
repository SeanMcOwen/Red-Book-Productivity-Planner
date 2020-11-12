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
    with sqlite3.connect(database_name) as conn:
        tasks = RedBook.Data.pull_tasks_SQL(conn)
    
    tables = ""
    for col in ["Today","Week","Month","Quarter","Year"]:
        temp = tasks[tasks[col]][['Task Name', 'Due Date', 'Group']]
        if len(temp) > 0:
            tables += "<h3>"+col+"</h3>"
            tables += """
            <table id="{}" class="display">
            <thead>
                <tr>
                    <th>Task Name</th>
                    <th>Due Date</th>
                    <th>Group</th>
                </tr>
            </thead>
            <tbody>
            """.format(col)
            for vals in temp.values:
                tables +=  """
                <tr>
                    <td>{}</td>
                    <td>{}</td>
                    <td>{}</td>
                </tr>
                """.format(vals[0], vals[1], vals[2])
            tables +=  """</tbody>
        </table>"""
            tables += "<br>"
        else:
            continue
    temp = tasks[['Task Name', 'Due Date', 'Group']]
    tables += "<h3>All Tasks</h3>"

    
    
    tables += """
    <table id="All" class="display">
    <thead>
        <tr>
            <th>Task Name</th>
            <th>Due Date</th>
            <th>Group</th>
        </tr>
    </thead>
    <tbody>
    """
    for vals in temp.values:
        tables +=  """
        <tr>
            <td>{}</td>
            <td>{}</td>
            <td>{}</td>
        </tr>
        """.format(vals[0], vals[1], vals[2])
    tables +=  """</tbody>
</table>"""
        

    
    return render_template("DataTables.html", tables=tables)
