from bokeh.embed import server_document
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Slider
from bokeh.plotting import figure
from bokeh.sampledata.sea_surface_temperature import sea_surface_temperature
from bokeh.server.server import Server
from bokeh.themes import Theme
from bokeh.models import ColumnDataSource, Select
import sqlite3
import RedBook

database_name = 'Goals.db'




    
def build_line_graph(goals, param_dictionary):
    data = goals.set_index('Goal Name').loc[param_dictionary['Goal Name'], 'Object'].daily_increment_tracker
    data = data.reset_index()
    data.columns = ['Date', 'Increment']
    source = ColumnDataSource(data=data)
    goal_select = Select(title="Goal:", value=param_dictionary['Goal Name'], options=list(goals['Goal Name']))

    
    p = figure(title = "{} Daily Increment".format(param_dictionary['Goal Name']),
               plot_width=400, plot_height=400, x_axis_type='datetime')
    p.line(x='Date', y='Increment', line_width=2, color='black', source=source)
    
    #Define the callback functions
    def callback_goal_name(attr, old, new):
        param_dictionary['Goal Name'] = new
        data = goals.set_index('Goal Name').loc[param_dictionary['Goal Name'], 'Object'].daily_increment_tracker
        data = data.reset_index()
        data.columns = ['Date', 'Increment']
    
        param_dictionary['Source'].data = ColumnDataSource.from_df(data)
        param_dictionary['Graph'].children[-1].title.text = "{} Daily Increment".format(param_dictionary['Goal Name'])
    goal_select.on_change('value', callback_goal_name)
    
    
    
    return column([goal_select, p]), source



    
def dailyIncrementsTracker(doc):
    with sqlite3.connect(database_name) as conn:
        goals, work_log = RedBook.Data.process_goals_SQL(conn)
        goals = goals[goals['Group'] != 'Fitness']
    goal_name = goals['Goal Name'].iloc[0]
    param_dictionary = {"Goal Name": goal_name,
                        "Goals": goals}
    graph, source = build_line_graph(goals, param_dictionary)
    param_dictionary['Source'] = source
    param_dictionary['Graph'] = graph


    doc.add_root(graph)
