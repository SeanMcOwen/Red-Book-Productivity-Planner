from bokeh.embed import server_document
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Slider, MultiLine
from bokeh.plotting import figure
from bokeh.sampledata.sea_surface_temperature import sea_surface_temperature
from bokeh.server.server import Server
from bokeh.themes import Theme
from bokeh.models import ColumnDataSource, Select
import sqlite3
import RedBook
import pandas as pd

database_name = 'Goals.db'


def pull_schedule_data(goals, goal_name, schedule_name):
    goal_object = goals.set_index('Goal Name').loc[goal_name, 'Object']
    graph_data = goal_object.compute_PIT_increments(schedule_name, expand_dates=False)
    graph_data2 = graph_data.copy()
    date_bump = .5
    new = schedule_name
    if new == 'Today':
            pass
    elif new == 'Week':
        date_bump = date_bump * 7
    elif new == 'Month':
        date_bump = date_bump * 30
    elif new == 'Quarter':
        date_bump = date_bump * 90
    graph_data2 = graph_data2.apply(lambda x: [[x['Start Date'] - pd.Timedelta("1D") * date_bump,
                                                x['Start Date'] + pd.Timedelta("1D") * date_bump],
                                               [x['Increment'], x['Increment']]], axis=1)
    graph_data2 = {"xs":graph_data2.apply(lambda x: x[0]).to_list(),
                                 "ys":graph_data2.apply(lambda x: x[1]).to_list()}
    return graph_data, graph_data2


    
def build_bar_graph(goals, schedule_data, goal_name, schedule_name, param_dictionary, graph_data2):
    source = ColumnDataSource(data=schedule_data)
    source2 = ColumnDataSource(data=graph_data2)
    goal_select = Select(title="Goal:", value=goal_name, options=list(goals['Goal Name']))
    schedule_select = Select(title="Schedule:", value="Historical", options=["Today",
                                                                             "Week", "Month", "Quarter"])
    
    p = figure(title = "{} {} Progress".format(goal_name, schedule_name),
               plot_width=400, plot_height=400, x_axis_type='datetime')
    vbar = p.vbar(x='Start Date', top='Progress', source=source, width=3600000*20)
    glyph = MultiLine(xs="xs", ys="ys", line_color="black", line_width=2)
    p.add_glyph(source2, glyph)
    
    #Define the callback functions
    def callback_goal_name(attr, old, new):
        param_dictionary['Goal Name'] = new
        schedule_data, graph_data2 = pull_schedule_data(param_dictionary['Goals'],
                                           param_dictionary['Goal Name'],
                                           param_dictionary['Schedule Name'])
    
        param_dictionary['Source'].data = ColumnDataSource.from_df(schedule_data)
        param_dictionary['Source2'].data = dict(ColumnDataSource(graph_data2).data)
        param_dictionary['Graph'].children[-1].title.text = "{} {} Progress".format(param_dictionary['Goal Name'], param_dictionary['Schedule Name'])
    goal_select.on_change('value', callback_goal_name)
    
    def callback_schedule(attr, old, new):
        param_dictionary['Schedule Name'] = new
        schedule_data, graph_data2  = pull_schedule_data(param_dictionary['Goals'],
                                           param_dictionary['Goal Name'],
                                           param_dictionary['Schedule Name'])
    
        param_dictionary['Source'].data = ColumnDataSource.from_df(schedule_data)
        param_dictionary['Source2'].data = dict(ColumnDataSource(graph_data2).data)
        param_dictionary['Graph'].children[-1].title.text = "{} {} Progress".format(param_dictionary['Goal Name'], param_dictionary['Schedule Name'])
        bar_size = 3600000*20
        if new == 'Today':
            pass
        elif new == 'Week':
            bar_size = bar_size * 7
        elif new == 'Month':
            bar_size = bar_size * 30
        elif new == 'Quarter':
            bar_size = bar_size * 90
        vbar.glyph.width = bar_size
    schedule_select.on_change('value', callback_schedule)
    

    
    if param_dictionary['GivenName']:
        return column([schedule_select, p]), source
    else:
        return column([goal_select, schedule_select,p]), source, source2



    
def progress_bars(doc):
    with sqlite3.connect(database_name) as conn:
        goals, work_log = RedBook.Data.process_goals_SQL(conn)
        goals = goals[goals['Group'] != 'Fitness']
    goal_name = goals['Goal Name'].iloc[0]
    
    

    schedule_name = "Today"
    param_dictionary = {"Goal Name": goal_name,
                        "Schedule Name": schedule_name,
                        "Goals": goals}
    param_dictionary['GivenName'] = False
    args = doc.session_context.request.arguments
    if 'goal_name' in args.keys():
        goal_name = str(args.get('goal_name')[0].decode("utf-8"))
        param_dictionary['GivenName'] = True
    schedule_data, graph_data2 = pull_schedule_data(goals, goal_name, schedule_name)
    graph, source, source2 = build_bar_graph(goals, schedule_data, goal_name, schedule_name, param_dictionary, graph_data2)
    param_dictionary['Source'] = source
    param_dictionary['Source2'] = source2
    param_dictionary['Graph'] = graph
    
    


    doc.add_root(graph)
