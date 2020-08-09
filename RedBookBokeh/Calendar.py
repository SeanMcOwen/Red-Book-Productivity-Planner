from bokeh.io import output_file, show
from bokeh.plotting import figure
from bokeh.sampledata.periodic_table import elements
from bokeh.transform import dodge, factor_cmap
import pandas as pd
from datetime import datetime
import calendar
import sqlite3
import RedBook
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Select, MultiLine
from calendar import Calendar
from calendar import day_abbr as day_abbrs
from calendar import month_name as month_names
    
from bokeh.document import Document
from bokeh.embed import file_html
from bokeh.layouts import gridplot
from bokeh.models import (CategoricalAxis, CategoricalScale, ColumnDataSource,
                              FactorRange, HoverTool, Plot, Rect, Text,)
from bokeh.resources import INLINE
from bokeh.util.browser import view
from bokeh.models import CheckboxButtonGroup

database_name = 'Goals.db'


def pull_calendar_data(goal, cal_choice):
    start_date = goal.start_date
    end_date = pd.to_datetime(datetime.now().date())
    dates = pd.date_range(start_date, end_date)
    data = pd.DataFrame(dates, columns= ['Date'])
    data['Year'] = data['Date'].dt.year
    data['Month'] = data['Date'].dt.month
    
    active_calendar_keys = cal_choice
    
    schedules = []
    overall_complete = []
    for key in active_calendar_keys:
        schedule = goal.compute_PIT_increments(key, expand_dates=True)
        overall_complete.append(schedule['Completed'])
        schedule.columns = key + " "+schedule.columns
        schedules.append(schedule)
    schedule = pd.concat(schedules,axis=1)
    schedule['Completed'] = pd.concat(overall_complete,axis=1).any(axis=1)
    
    data = data.join(schedule, on=['Date'])
    data['Color'] = data['Completed'].fillna(-1).astype(int).map({1: 'green',
                                                      0: 'red',
                                                      -1: 'grey'})
    return data
    
    
def make_calendar(year, month, data, firstweekday="Mon"):
    firstweekday = list(day_abbrs).index(firstweekday)
    calendar = Calendar(firstweekday=firstweekday)
    
    month_days  = [ None if not day else str(day) for day in calendar.itermonthdays(year, month) ]
    month_weeks = len(month_days)//7
    
    workday = "linen"
    weekend = "lightsteelblue"
    
    def weekday(date):
        return (date.weekday() - firstweekday) % 7
    
    def pick_weekdays(days):
        return [ days[i % 7] for i in range(firstweekday, firstweekday+7) ]
        
    
    day_names = pick_weekdays(day_abbrs)
    week_days = pick_weekdays([workday]*5 + [weekend]*2)
        
    def background_color(x,year, month, data):
        if x is None:
            return "grey"
        elif pd.to_datetime(datetime(year,month, int(x))) in list(data['Date'].values):
            if data.set_index('Date').loc[pd.to_datetime(datetime(year,month, int(x))), 'Completed']:
                return "green"
            else:
                return 'red'
        else:
            return 'grey'
    
    def add_hover_thing(x, year, month, data, d_key):
        if x is None:
            return ""
        elif pd.to_datetime(datetime(year,month, int(x))) in list(data['Date'].values):
            return data.set_index('Date').loc[pd.to_datetime(datetime(year,month, int(x))), d_key]

        
        
    m_data = dict(
            days            = list(day_names)*month_weeks,
            weeks           = sum([ [str(week)]*7 for week in range(month_weeks) ], []),
            month_days      = month_days,
            day_backgrounds = [background_color(x,year, month, data) for x in month_days]
        )
    hover_keys = []
    for d_key in data.columns:
        if 'Increment' in d_key or 'Progress' in d_key:
            m_data[d_key.replace(" ","_")] = [add_hover_thing(x,year, month, data, d_key) for x in month_days]
            hover_keys.append((d_key, "@"+d_key.replace(" ","_")))
    #m_data['today_increment'] = [add_hover_thing(x,year, month, data) for x in month_days]
        
    source = ColumnDataSource(m_data)
    

    
    xdr = FactorRange(factors=list(day_names))
    ydr = FactorRange(factors=list(reversed([ str(week) for week in range(month_weeks) ])))
    x_scale, y_scale = CategoricalScale(), CategoricalScale()
    
    plot = Plot(x_range=xdr, y_range=ydr, x_scale=x_scale, y_scale=y_scale,
                    plot_width=300, plot_height=300, outline_line_color=None)
    plot.title.text = month_names[month]
    plot.title.text_font_size = "16px"
    plot.title.text_color = "darkolivegreen"
    plot.title.offset = 25
    plot.min_border_left = 0
    plot.min_border_bottom = 5
    
    rect = Rect(x="days", y="weeks", width=0.9, height=0.9, fill_color="day_backgrounds", line_color="silver")
    plot.add_glyph(source, rect)
    

    
    text = Text(x="days", y="weeks", text="month_days", text_align="center", text_baseline="middle")
    plot.add_glyph(source, text)
    
    xaxis = CategoricalAxis()
    xaxis.major_label_text_font_size = "11px"
    xaxis.major_label_standoff = 0
    xaxis.major_tick_line_color = None
    xaxis.axis_line_color = None
    plot.add_layout(xaxis, 'above')
    
    hover_tool = HoverTool(tooltips=hover_keys)
    plot.tools.append(hover_tool)
    plot.toolbar_location = None
    
    return plot


def build_cals(goal, cal_choice):
    data = pull_calendar_data(goal, cal_choice)
    temp = data.groupby(['Year', 'Month']).size().reset_index()
    temp = [temp[i:i+3] for i in range(0, len(temp), 3)]
    months = [[make_calendar(x.loc[x1].iloc[0], x.loc[x1].iloc[1], data) for x1 in x.index] for x in temp]
    return months


def calendar_view(doc):
    
    
    
    with sqlite3.connect(database_name) as conn:
        goals, work_log = RedBook.Data.process_goals_SQL(conn)
        goals = goals[goals['Group'] != 'Fitness']
    goal_name = goals.iloc[0]['Goal Name']
    goal = goals.set_index('Goal Name').loc[goal_name, 'Object']
    
    cal_choice = ['Today']
    months = build_cals(goal, cal_choice)
    
    months_l = []
    for m in months:
        months_l.extend(m)

    grid = gridplot(toolbar_location=None, children=months_l, ncols=3)
    
    
    
    goal_select = Select(title="Goal:", value=goal_name, options=list(goals['Goal Name']))
    calendar_select = CheckboxButtonGroup(
        labels=["Today", "Week", "Month", "Quarter", "Year"], active=[0])
    
    param_dictionary = {}
    param_dictionary['Grid'] = grid
    param_dictionary['Goal Name'] = goal_name
    param_dictionary['Goals'] = goals
    param_dictionary['cal_choice'] = ['Today']
    
    def callback_goal_name(attr, old, new):
        param_dictionary['Goal Name'] = new
        
        goal = goals.set_index('Goal Name').loc[param_dictionary['Goal Name'], 'Object']
        months = build_cals(goal, param_dictionary['cal_choice'])
        months_l = []
        for i, m in enumerate(months):
            if len(m) > 2:
                months_l.append((m[0], i, 0))
                months_l.append((m[1], i, 1))
                months_l.append((m[2], i, 2))
            elif len(m) > 1:
                months_l.append((m[0], i, 0))
                months_l.append((m[1], i, 1))
                #months_l.append((None, i, 2))
            else:
                months_l.append((m[0], i, 0))
                #months_l.append((None, i, 1))
                #months_l.append((None, i, 2))
        param_dictionary['Grid'].children = months_l
    
    def callback_calendar(attr, old, new):
        cal_choice = [["Today", "Week", "Month", "Quarter", "Year"][x] for x in new]
        param_dictionary['cal_choice'] = cal_choice
        goal = goals.set_index('Goal Name').loc[param_dictionary['Goal Name'], 'Object']
        months = build_cals(goal, param_dictionary['cal_choice'])
        months_l = []
        for i, m in enumerate(months):
            if len(m) > 2:
                months_l.append((m[0], i, 0))
                months_l.append((m[1], i, 1))
                months_l.append((m[2], i, 2))
            elif len(m) > 1:
                months_l.append((m[0], i, 0))
                months_l.append((m[1], i, 1))
                #months_l.append((None, i, 2))
            else:
                months_l.append((m[0], i, 0))
                #months_l.append((None, i, 1))
                #months_l.append((None, i, 2))
        param_dictionary['Grid'].children = months_l
    goal_select.on_change('value', callback_goal_name)
    calendar_select.on_change('active', callback_calendar)
    
    doc.add_root(column([row(goal_select, calendar_select), grid]))
    
    

