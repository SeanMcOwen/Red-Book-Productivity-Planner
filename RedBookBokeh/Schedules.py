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


def pull_schedule_data(goals, goal_name, schedule_name, date_range):
    goal_object = goals.set_index('Goal Name').loc[goal_name, 'Object']
    graph_data = goal_object.graph_progress(schedule_name, date_range=date_range, action='data')
    graph_data.index.name = 'Date'
    return graph_data


    
def build_line_graph(goals, schedule_data, goal_name, schedule_name, param_dictionary):
    source = ColumnDataSource(data=schedule_data)
    goal_select = Select(title="Goal:", value=goal_name, options=list(goals['Goal Name']))
    schedule_select = Select(title="Schedule:", value="Historical", options=["Historical", "Today",
                                                                             "Week", "Month", "Quarter",
                                                                             "Year"])
    date_range_select = Select(title="Date Range:", value="Overlap", options=["Overlap", "Full", "Goal Period"])
    
    p = figure(title = "{} {} Schedule".format(goal_name, schedule_name),
               plot_width=400, plot_height=400, x_axis_type='datetime')
    p.line(x='Date', y='Schedule', line_width=2, color='grey', source=source)
    p.line(x='Date', y='Progress', line_width=2, color='red', source=source)
    
    #Define the callback functions
    def callback_goal_name(attr, old, new):
        param_dictionary['Goal Name'] = new
        schedule_data = pull_schedule_data(param_dictionary['Goals'],
                                           param_dictionary['Goal Name'],
                                           param_dictionary['Schedule Name'],
                                           param_dictionary['Date Range'])
    
        param_dictionary['Source'].data = ColumnDataSource.from_df(schedule_data)
        param_dictionary['Graph'].children[-1].title.text = "{} {} Schedule".format(param_dictionary['Goal Name'], param_dictionary['Schedule Name'])
    goal_select.on_change('value', callback_goal_name)
    
    def callback_schedule(attr, old, new):
        param_dictionary['Schedule Name'] = new
        schedule_data = pull_schedule_data(param_dictionary['Goals'],
                                           param_dictionary['Goal Name'],
                                           param_dictionary['Schedule Name'],
                                           param_dictionary['Date Range'])
    
        param_dictionary['Source'].data = ColumnDataSource.from_df(schedule_data)
        param_dictionary['Graph'].children[-1].title.text = "{} {} Schedule".format(param_dictionary['Goal Name'], param_dictionary['Schedule Name'])
    schedule_select.on_change('value', callback_schedule)
    
    def callback_date_range(attr, old, new):
        param_dictionary['Date Range'] = new
        schedule_data = pull_schedule_data(param_dictionary['Goals'],
                                           param_dictionary['Goal Name'],
                                           param_dictionary['Schedule Name'],
                                           param_dictionary['Date Range'])
    
        param_dictionary['Source'].data = ColumnDataSource.from_df(schedule_data)
        param_dictionary['Graph'].children[-1].title.text = "{} {} Schedule".format(param_dictionary['Goal Name'], param_dictionary['Schedule Name'])
    date_range_select.on_change('value', callback_date_range)
    
    if param_dictionary['GivenName']:
        return column([schedule_select, date_range_select, p]), source
    else:
        return column([goal_select, schedule_select, date_range_select,p]), source



    
def schedules(doc):
    with sqlite3.connect(database_name) as conn:
        goals, work_log = RedBook.Data.process_goals_SQL(conn)
        goals = goals[goals['Group'] != 'Fitness']
    goal_name = goals['Goal Name'].iloc[0]
    
    

    schedule_name = "Historical"
    date_range = "Overlap"
    param_dictionary = {"Goal Name": goal_name,
                        "Schedule Name": schedule_name,
                        "Date Range": date_range,
                        "Goals": goals}
    param_dictionary['GivenName'] = False
    args = doc.session_context.request.arguments
    if 'goal_name' in args.keys():
        goal_name = str(args.get('goal_name')[0].decode("utf-8"))
        param_dictionary['GivenName'] = True
        param_dictionary["Goal Name"] =  goal_name
    schedule_data = pull_schedule_data(goals, goal_name, schedule_name, date_range)
    graph, source = build_line_graph(goals, schedule_data, goal_name, schedule_name, param_dictionary)
    param_dictionary['Source'] = source
    param_dictionary['Graph'] = graph
    
    


    doc.add_root(graph)
