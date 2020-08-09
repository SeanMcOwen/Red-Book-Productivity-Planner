from bokeh.embed import server_document
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Slider
from bokeh.plotting import figure
from bokeh.sampledata.sea_surface_temperature import sea_surface_temperature
from bokeh.server.server import Server
from bokeh.themes import Theme
from bokeh.models import ColumnDataSource, Select, MultiLine
import sqlite3
import RedBook

database_name = 'Goals.db'


def pull_schedule_data(goals, goal_name, schedule_name, date_range):
    goal_object = goals.set_index('Goal Name').loc[goal_name, 'Object']
    graph_data = goal_object.compute_PIT_schedules(schedule_name, date_range)
    graph_data = {"Date":[x.index for x in graph_data],
                  "Schedule":[x.values for x in graph_data]}
    temp = goals.set_index('Goal Name').loc[goal_name, 'Object'].progress_log.reset_index()
    temp.columns = ['Date', 'Progress']
    graph_data2 = temp
    return graph_data, graph_data2


    
def build_line_graph(goals, schedule_data, goal_name, schedule_name, param_dictionary, graph_data2):
    
    source = ColumnDataSource(schedule_data)
    source2 = ColumnDataSource(data=graph_data2)
    goal_select = Select(title="Goal:", value=goal_name, options=list(goals['Goal Name']))
    schedule_select = Select(title="Schedule:", value="Week", options=["Today",
                                                                             "Week", "Month", "Quarter",
                                                                             "Year"])
    date_range_select = Select(title="Date Range:", value="Overlap", options=["Overlap", "Full", "Goal Period"])
    
    p = figure(title = "{} {} Schedule".format(goal_name, schedule_name),
               plot_width=400, plot_height=400, x_axis_type='datetime')
    #p.line(x='Date', y='Schedule', line_width=2, color='grey', source=source)
    glyph = MultiLine(xs="Date", ys="Schedule", line_color="grey", line_width=2)
    p.add_glyph(source, glyph)
    p.line(x='Date', y='Progress', line_width=2, color='red', source=source2)
    
    #Define the callback functions
    def callback_goal_name(attr, old, new):
        param_dictionary['Goal Name'] = new
        schedule_data, graph_data2 = pull_schedule_data(param_dictionary['Goals'],
                                           param_dictionary['Goal Name'],
                                           param_dictionary['Schedule Name'],
                                           param_dictionary['Date Range'])
    
        param_dictionary['Source'].data = schedule_data
        param_dictionary['Source2'].data = ColumnDataSource.from_df(graph_data2)
        param_dictionary['Graph'].children[-1].title.text = "{} {} Schedule".format(param_dictionary['Goal Name'], param_dictionary['Schedule Name'])
    goal_select.on_change('value', callback_goal_name)
    
    def callback_schedule(attr, old, new):
        param_dictionary['Schedule Name'] = new
        schedule_data, graph_data2 = pull_schedule_data(param_dictionary['Goals'],
                                           param_dictionary['Goal Name'],
                                           param_dictionary['Schedule Name'],
                                           param_dictionary['Date Range'])
    
        param_dictionary['Source'].data = schedule_data
        param_dictionary['Source2'].data = ColumnDataSource.from_df(graph_data2)
        param_dictionary['Graph'].children[-1].title.text = "{} {} Schedule".format(param_dictionary['Goal Name'], param_dictionary['Schedule Name'])
    schedule_select.on_change('value', callback_schedule)
    
    def callback_date_range(attr, old, new):
        param_dictionary['Date Range'] = new
        schedule_data, graph_data2 = pull_schedule_data(param_dictionary['Goals'],
                                           param_dictionary['Goal Name'],
                                           param_dictionary['Schedule Name'],
                                           param_dictionary['Date Range'])
    
        param_dictionary['Source'].data = schedule_data
        param_dictionary['Source2'].data = ColumnDataSource.from_df(graph_data2)
        param_dictionary['Graph'].children[-1].title.text = "{} {} Schedule".format(param_dictionary['Goal Name'], param_dictionary['Schedule Name'])
    date_range_select.on_change('value', callback_date_range)
    
    
    return column([goal_select, schedule_select, date_range_select,p]), source, source2


def schedules_PIT(doc):
    with sqlite3.connect(database_name) as conn:
        goals, work_log = RedBook.Data.process_goals_SQL(conn)
        goals = goals[goals['Group'] != 'Fitness']
    goal_name = goals['Goal Name'].iloc[0]
    schedule_name = "Week"
    date_range = "Overlap"
    param_dictionary = {"Goal Name": goal_name,
                        "Schedule Name": schedule_name,
                        "Date Range": date_range,
                        "Goals": goals}
    schedule_data, graph_data2 = pull_schedule_data(goals, goal_name, schedule_name, date_range)
    graph, source, source2 = build_line_graph(goals, schedule_data, goal_name, schedule_name, param_dictionary, graph_data2)
    param_dictionary['Source'] = source
    param_dictionary['Source2'] = source2
    param_dictionary['Graph'] = graph


    doc.add_root(graph)
    
