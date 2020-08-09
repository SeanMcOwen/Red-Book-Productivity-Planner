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
from bokeh.layouts import gridplot, Spacer
from bokeh.models import (CategoricalAxis, CategoricalScale, ColumnDataSource,
                              FactorRange, HoverTool, Plot, Rect, Text,)
from bokeh.resources import INLINE
from bokeh.util.browser import view
from bokeh.models import CheckboxButtonGroup, Button

database_name = 'Goals.db'


def create_schedule_data(data, dates, group):
    data_mini = data.copy()
    data_mini = data_mini[data_mini['Date'].isin(dates)]
    num_goals = len(group.data['Goal Name'])
    num_days = len(dates)
    
    goal_i = []
    for i in range(num_goals):
        goal_i.extend([group.data['Goal Name'].iloc[i]]*num_days)
    
    temp = data.set_index(['Date', 'Goal Name'])
    def background_color(data, date, goal):
        if (date, goal) not in data.index:
            return "grey"
        else:
            if data.loc[(date, goal), 'Completed'].values[0]:
                return "green"
            else:
                return 'red'
    
    def completed_l(data, date, goal):
        if (date, goal) not in data.index:
            return ""
        else:
            if data.loc[(date, goal), 'Completed'].values[0]:
                return "True"
            else:
                return "False"
    
    def hover_l(data, date, goal, l1, l2, l3, l4, l5):
        if (date, goal) not in data.index:
            for l in [l1,l2,l3,l4,l5]:
                l.append("")
        else:
            temp = data.loc[(date, goal)]
            l1.append(temp.loc['Progress'])
            l2.append(temp.loc['Current Progress'])
            l3.append(temp.loc['Work Required'])
            l4.append(temp.loc['Work Done'])
            l5.append(max(abs(temp.loc['Work Required'])-abs(temp.loc['Work Done']), 0))
            
            
    m_data = dict(
                days            = list(dates.strftime("%m/%d/%y")) * num_goals,
                goal_i           = goal_i,
                month_days      = list(dates.strftime("%m/%d/%y")) * num_goals,
            )
    day_backgrounds = []
    completed_lists = []
    l1, l2, l3, l4, l5 = [], [], [], [], []
    for a,b in zip(m_data['days'], m_data['goal_i']):
        day_backgrounds.append(background_color(temp,a,b))
        completed_lists.append(completed_l(temp, a, b))
        hover_l(temp, a, b, l1, l2, l3, l4, l5)
    m_data['day_backgrounds'] = day_backgrounds
    m_data['Completed'] = completed_lists
    m_data['Expected_Progress'] = l1
    m_data['Current_Progress'] = l2
    m_data['Work_Required'] = l3
    m_data['Work_Done'] = l4
    m_data['Work_Left'] = l5
    
    
    
    

    return m_data
    
    
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


def build_calendar(group, param_dictionary):
    xdr = FactorRange(factors=list(param_dictionary['dates'].strftime("%m/%d/%y")))
    ydr = FactorRange(factors=list(reversed(param_dictionary['Group'].data['Goal Name'].values)))
    x_scale, y_scale = CategoricalScale(), CategoricalScale()    
    plot = Plot(x_range=xdr, y_range=ydr, x_scale=x_scale, y_scale=y_scale,
                plot_width=1200, plot_height=300, outline_line_color=None)
    source = ColumnDataSource(param_dictionary['schedule_data'])
    param_dictionary['Source'] = source
    rect = Rect(x="days", y="goal_i", width=0.9, height=0.9, fill_color="day_backgrounds", line_color="silver")
    plot.add_glyph(source, rect)
    

    
    plot.min_border_left = 0
    plot.min_border_bottom = 5
    
    xaxis = CategoricalAxis()
    xaxis.major_label_text_font_size = "16px"
    xaxis.major_label_standoff = 0
    xaxis.major_tick_line_color = None
    xaxis.axis_line_color = None
    plot.add_layout(xaxis, 'above')
    
    yaxis = CategoricalAxis()
    yaxis.major_label_text_font_size = "16px"
    yaxis.major_label_standoff = 0
    yaxis.major_tick_line_color = None
    yaxis.axis_line_color = None
    plot.add_layout(yaxis, 'left')
    

    
    hover_keys = [('Expected Progress', '@Expected_Progress'),
                  ('Current Progress', '@Current_Progress'),
                  ('Work Required', '@Work_Required'),
                  ('Work Done', '@Work_Done'),
                  ('Work Left', '@Work_Left')]
    hover_tool = HoverTool(tooltips=hover_keys)
    plot.tools.append(hover_tool)
    plot.toolbar_location = None
    
    return plot

def GroupCalendarProgress(doc):
    
    
    
    with sqlite3.connect(database_name) as conn:
        goals, work_log = RedBook.Data.process_goals_SQL(conn)
        goals = goals[goals['Group'] != 'Fitness']
    group_name = goals['Group'].unique()[0]
    group = RedBook.Classes.Group(goals[goals['Group'] == group_name])
    cal_choice = 'Week'
    data = group.build_group_schedule(cal_choice, data_type = 'Completion')
    start_date = max(data['Date'].min(), pd.to_datetime(datetime.now().date()) - pd.Timedelta("4D"))
    end_date = start_date + pd.Timedelta("8D")
    dates = pd.date_range(start_date, end_date)
    
    param_dictionary = {}
    param_dictionary['Group Name'] = group_name
    param_dictionary['Goals'] = goals
    param_dictionary['Group'] = group
    param_dictionary['cal_choice'] = cal_choice
    param_dictionary['start_date'] = start_date
    param_dictionary['end_date'] = end_date
    param_dictionary['dates'] = dates
    param_dictionary['schedule_data'] = create_schedule_data(data, dates, group)
    param_dictionary['data'] = data

    goal_select = Select(title="Group:", value=group_name, options=list(goals['Group'].unique())+['All'])
    calendar_select = Select(title="Calendar:", value=cal_choice, options=["Today", "Week", "Month", "Quarter", "Year", "Historical"])
    toggle_backward = Button(label="<-", button_type="success")
    toggle_forward = Button(label="->", button_type="success")
    jump_ahead = Button(label="Jump to Non-Complete", button_type="success")
    
    def callback_forward():
        temp = param_dictionary['start_date'] + pd.Timedelta("1D")
        param_dictionary['start_date'] = max(param_dictionary['data']['Date'].min(), temp)
        param_dictionary['end_date'] = param_dictionary['start_date'] + pd.Timedelta("8D")
        param_dictionary['dates'] = pd.date_range(param_dictionary['start_date'], param_dictionary['end_date'])
        param_dictionary['schedule_data'] = create_schedule_data(param_dictionary['data'], param_dictionary['dates'], param_dictionary['Group'])
        param_dictionary['Source'].data = param_dictionary['schedule_data']
        param_dictionary['plot'].x_range.factors = list(param_dictionary['dates'].strftime("%m/%d/%y"))
        
    def callback_backward():
        temp = param_dictionary['start_date'] - pd.Timedelta("1D")
        param_dictionary['start_date'] = max(param_dictionary['data']['Date'].min(), temp)
        param_dictionary['end_date'] = param_dictionary['start_date'] + pd.Timedelta("8D")
        param_dictionary['dates'] = pd.date_range(param_dictionary['start_date'], param_dictionary['end_date'])
        param_dictionary['schedule_data'] = create_schedule_data(param_dictionary['data'], param_dictionary['dates'], param_dictionary['Group'])
        param_dictionary['Source'].data = param_dictionary['schedule_data']
        param_dictionary['plot'].x_range.factors = list(param_dictionary['dates'].strftime("%m/%d/%y"))
    
    def callback_jump_forward():
        date = param_dictionary['data']
        date = date[~date['Completed']]
        date = date['Date'].min()
        param_dictionary['start_date'] = date
        param_dictionary['end_date'] = param_dictionary['start_date'] + pd.Timedelta("8D")
        param_dictionary['dates'] = pd.date_range(param_dictionary['start_date'], param_dictionary['end_date'])
        param_dictionary['schedule_data'] = create_schedule_data(param_dictionary['data'], param_dictionary['dates'], param_dictionary['Group'])
        param_dictionary['Source'].data = param_dictionary['schedule_data']
        param_dictionary['plot'].x_range.factors = list(param_dictionary['dates'].strftime("%m/%d/%y"))
        
    
    toggle_backward.on_click(callback_backward)
    toggle_forward.on_click(callback_forward)
    jump_ahead.on_click(callback_jump_forward)

    
    def callback_goal_name(attr, old, new):
        
        param_dictionary['Group Name'] = new
        group_name = goals['Group'].unique()[0]
        if new == 'All':
            group = RedBook.Classes.Group(goals)
        else:
            group = RedBook.Classes.Group(goals[goals['Group'] == new])
        cal_choice = param_dictionary['cal_choice']
        data = group.build_group_schedule(cal_choice, data_type = 'Completion')
        start_date = max(data['Date'].min(), pd.to_datetime(datetime.now().date()) - pd.Timedelta("4D"))
        end_date = start_date + pd.Timedelta("8D")
        dates = pd.date_range(start_date, end_date)
        param_dictionary['Group'] = group
        param_dictionary['start_date'] = start_date
        param_dictionary['end_date'] = end_date
        param_dictionary['dates'] = dates
        param_dictionary['schedule_data'] = create_schedule_data(data, dates, group)
        param_dictionary['data'] = data
        param_dictionary['Source'].data = param_dictionary['schedule_data']
        param_dictionary['plot'].x_range.factors = list(param_dictionary['dates'].strftime("%m/%d/%y"))
        param_dictionary['plot'].y_range.factors = list(reversed(param_dictionary['Group'].data['Goal Name'].values))
    
    goal_select.on_change('value', callback_goal_name)
        

    def callback_calendar(attr, old, new):
        param_dictionary['cal_choice'] = new
        
        if param_dictionary['Group Name'] == 'All':
            group = RedBook.Classes.Group(goals)
        else:
            group = RedBook.Classes.Group(goals[goals['Group'] == param_dictionary['Group Name']])
        cal_choice = param_dictionary['cal_choice']
        data = group.build_group_schedule(cal_choice, data_type = 'Completion')
        start_date = max(data['Date'].min(), pd.to_datetime(datetime.now().date()) - pd.Timedelta("4D"))
        end_date = start_date + pd.Timedelta("8D")
        dates = pd.date_range(start_date, end_date)
        param_dictionary['Group'] = group
        param_dictionary['start_date'] = start_date
        param_dictionary['end_date'] = end_date
        param_dictionary['dates'] = dates
        param_dictionary['schedule_data'] = create_schedule_data(data, dates, group)
        param_dictionary['data'] = data
        param_dictionary['Source'].data = param_dictionary['schedule_data']
        param_dictionary['plot'].x_range.factors = list(param_dictionary['dates'].strftime("%m/%d/%y"))
        param_dictionary['plot'].y_range.factors = list(reversed(param_dictionary['Group'].data['Goal Name'].values))
    
    calendar_select.on_change('value', callback_calendar)
    
    plot = build_calendar(group, param_dictionary)
    param_dictionary['plot'] = plot
    doc.add_root(column([row(goal_select),
                         row(calendar_select),
                         row(Spacer(height=25)),
                         row(jump_ahead),
                         row(toggle_backward, Spacer(width=575), toggle_forward), plot]))
    
    

