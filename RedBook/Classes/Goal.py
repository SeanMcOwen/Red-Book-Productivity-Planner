import pandas as pd
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

def create_schedule(start_progress, goal_progress, start_date, end_date):
    schedule = pd.Series(np.NaN, index=pd.date_range(start_date-pd.Timedelta("1D"), end_date))
    
    schedule.iloc[0] = start_progress
    schedule.iloc[-1] = goal_progress
    
    schedule = schedule.interpolate()
    return schedule

def build_date_dictionary(start_date, end_date):
    today = pd.to_datetime(datetime.now().date())
    date_dictionary = {"Today": today}
    date_dictionary['Week'] = today - pd.Timedelta("{}D".format(today.weekday()))
    date_dictionary['Month'] = datetime(today.year, today.month, 1)
    date_dictionary['Quarter'] = datetime(today.year, 1+(today.quarter-1)*3, 1)
    date_dictionary['Year'] = datetime(today.year, 1, 1)
    
    date_dictionary_next = {}
    date_dictionary_next['Today'] = date_dictionary['Today']
    date_dictionary_next['Week'] = date_dictionary['Week'] + pd.Timedelta("6D")
    
    month = (date_dictionary['Month'].month % 12) + 1
    if date_dictionary['Month'].month == 12:
        year = date_dictionary['Month'].year + 1
    else:
        year = date_dictionary['Month'].year
    date_dictionary_next['Month'] = datetime(year, month, 1) - pd.Timedelta("1D")
    
    month = date_dictionary['Quarter'].month
    if date_dictionary['Quarter'].month == 10:
        year = date_dictionary['Month'].year + 1
        month = 1
    else:
        year = date_dictionary['Month'].year
        month = month + 3
    date_dictionary_next['Quarter'] = datetime(year, month, 1) - pd.Timedelta("1D")
    
    date_dictionary_next['Year'] = datetime(date_dictionary['Year'].year+1, 1, 1) - pd.Timedelta("1D")
    
    date_dictionary['Week'] = pd.to_datetime(max(date_dictionary['Week'], start_date))
    date_dictionary['Month'] = pd.to_datetime(max(date_dictionary['Month'], start_date))
    date_dictionary['Quarter'] = pd.to_datetime(max(date_dictionary['Quarter'], start_date))
    date_dictionary['Year'] = pd.to_datetime(max(date_dictionary['Year'], start_date))

    date_dictionary_next['Week'] = pd.to_datetime(min(date_dictionary_next['Week'], end_date))
    date_dictionary_next['Month'] = pd.to_datetime(min(date_dictionary_next['Month'], end_date))
    date_dictionary_next['Quarter'] = pd.to_datetime(min(date_dictionary_next['Quarter'], end_date))
    date_dictionary_next['Year'] = pd.to_datetime(min(date_dictionary_next['Year'], end_date))

    
    return date_dictionary, date_dictionary_next


def build_date_dictionary_increments(date_dictionary, progress_log):
    date_dictionary_increments = {}
    for key in date_dictionary.keys():
        date_dictionary_increments[key] = progress_log.loc[date_dictionary[key] - pd.Timedelta("1D")]
    return date_dictionary_increments

def find_dates_schedule(goal, schedule_key):
    today = pd.to_datetime(datetime.now().date())
    if schedule_key == 'Today':
        dates = pd.date_range(goal.start_date, today)
    elif schedule_key == 'Week':
        dates = pd.date_range(goal.start_date, today)
        dates = dates[dates.weekday == 0]
    elif schedule_key == 'Month':
        dates = pd.date_range(goal.start_date, today)
        dates = dates[dates.day == 1]
    elif schedule_key == 'Quarter':
        dates = pd.date_range(goal.start_date, today)
        dates = dates[dates.day == 1]
        dates = dates[dates.month.isin([1,4,7,10])]
    elif schedule_key == 'Year':
        dates = pd.date_range(goal.start_date, today)
        dates = dates[(dates.day == 1) & (dates.month == 1)]
    else:
        assert False
    dates = [goal.start_date] + list(dates)
    dates = list(set(dates))
    dates = pd.to_datetime(sorted(dates))
    return dates

def compute_PIT_schedule(goal, dates):
    schedules = []
    for x in range(len(dates)-1):
        start_date = dates[x]
        end_date_s = dates[x+1]-pd.Timedelta("1D")
        end_date = goal.end_date
        goal_progress = goal.end_progress
        start_progress = goal.progress_log.loc[start_date - pd.Timedelta("1D")]
        schedule = create_schedule(start_progress, goal_progress, start_date, end_date)
        schedules.append(schedule.loc[start_date-pd.Timedelta("1D"):end_date_s])
    start_date = dates[-1]
    end_date = goal.end_date
    goal_progress = goal.end_progress
    start_progress = goal.progress_log.loc[start_date - pd.Timedelta("1D")]
    schedule = create_schedule(start_progress, goal_progress, start_date, end_date)
    schedules.append(schedule.loc[start_date-pd.Timedelta("1D"):])
    return schedules


class Goal:
    def __init__(self, goal_params, progress_log):
        self.increment_flags = {}
        self.increment_flags['Today'] = goal_params['Today']
        self.increment_flags['Week'] = goal_params['Week']
        self.increment_flags['Month'] = goal_params['Month']
        self.increment_flags['Quarter'] = goal_params['Quarter']
        self.increment_flags['Year'] = goal_params['Year']
        self.increment_flags['Historical'] = goal_params['Historical']
        self.number = goal_params['Goal #']
        self.name = goal_params['Goal Name']
        self.progress_name = goal_params['Progress Name']
        
        self.end_progress = goal_params['Goal Progress']
        self.group = goal_params['Group']
        self.progress_log = progress_log
        self.progress_type = goal_params['Progress Type']
        self.start_date = goal_params['Start Date']
        self.end_date = goal_params['End Date']
        

        self.current_progress = progress_log.iloc[-1]
        self.progress_log = progress_log.reindex(pd.date_range(progress_log.index[0], pd.to_datetime(datetime.today().date())))
        self.progress_log = self.progress_log.fillna(method='ffill')
        self.progress_log = self.progress_log.reindex(pd.date_range(self.start_date-pd.Timedelta("1D"), pd.to_datetime(datetime.today().date())))
        self.start_progress = self.progress_log[goal_params['Start Date'] - pd.Timedelta("1D")]
        self.progress_log = self.progress_log.fillna(self.start_progress)

        
        self.build_schedules()
        self.build_daily_increment_tracker()
    
    def graph_progress(self, schedule_name, date_range='Overlap', action='matplotlib'):
        graph_data = pd.concat([self.schedules[schedule_name], self.progress_log], axis=1)
        if date_range=='Overlap':
            graph_data = graph_data.dropna()
        elif date_range == 'Full':
            pass
        elif date_range == 'Goal Period':
            graph_data = graph_data.loc[self.date_dictionary[schedule_name]-pd.Timedelta("1D"):self.date_dictionary_next[schedule_name]]
        else:
            assert False
        
        graph_data.columns = ['Schedule', 'Progress']
        if action == 'matplotlib':
            graph_data.plot(kind='line')
            plt.show()
        elif action == 'data':
            return graph_data
        else:
            assert False
        
    def build_schedules(self):
        today = pd.to_datetime(datetime.now().date())
        self.date_dictionary, self.date_dictionary_next = build_date_dictionary(self.start_date, self.end_date)
        self.date_dictionary['Historical'] = self.start_date
        self.date_dictionary_next['Historical'] = self.end_date
        self.date_dictionary_increments = build_date_dictionary_increments(self.date_dictionary, self.progress_log)
        
        self.schedules = {}
        self.schedule_goals = {}
        self.increments = {}
        self.increments_percent = {}
        self.schedule_goals_today = {}
        self.increments_today = {}
        self.schedules['Historical'] = create_schedule(self.start_progress, self.end_progress, self.start_date, self.end_date)
        for key in self.date_dictionary.keys():
            self.schedules[key] = create_schedule(self.date_dictionary_increments[key], self.end_progress, self.date_dictionary[key], self.end_date)
            self.schedule_goals[key] = self.schedules[key].loc[min(self.end_date, self.date_dictionary_next[key])]
            self.schedule_goals_today[key] = self.schedules[key].loc[today]
            self.increments[key] = self.schedule_goals[key] - self.current_progress
            self.increments_today[key] = self.schedule_goals_today[key] - self.current_progress
            self.increments_percent[key] = (self.schedule_goals[key] - self.current_progress) / (self.schedule_goals[key] - self.schedules[key].iloc[0])
            if abs(self.schedule_goals[key] - self.schedules[key].iloc[0]) < abs(self.current_progress - self.schedules[key].iloc[0]):
                self.increments[key] = np.NaN
                self.increments_percent[key] = np.NaN
            if abs(self.schedule_goals_today[key] - self.schedules[key].iloc[0]) < abs(self.current_progress - self.schedules[key].iloc[0]):
                self.increments_today[key] = np.NaN
        if pd.isnull(pd.Series(self.increments_today)).all():
            self.increments_today['Maximum'] = np.NaN
        else:
            self.increments_today['Maximum'] = pd.Series(self.increments_today).max()
        
                
        self.effective_schedule_dates = {}
        for key in self.schedules.keys():
            schedule = self.schedules[key] <= self.current_progress
            self.effective_schedule_dates[key] = schedule[schedule].index.max()
            
    def build_daily_increment_tracker(self):
        progress_left = (self.end_progress - self.progress_log)
        days = (self.end_date - progress_left.index).days - 1
        daily_increments_tracker = progress_left / days
        daily_increments_tracker.index = daily_increments_tracker.index + pd.Timedelta("1D")
        self.daily_increment_tracker = daily_increments_tracker
    
    def compute_PIT_schedules(self, schedule_key, date_range):
        dates = find_dates_schedule(self, schedule_key)
        schedules = compute_PIT_schedule(self, dates)
        today = pd.to_datetime(datetime.now().date())
        if date_range=='Overlap':
            for i in range(len(schedules)):
                schedules[i] = schedules[i].loc[self.start_date-pd.Timedelta('1D'):today]
        elif date_range == 'Full':
            pass
        elif date_range == 'Goal Period':
            for i in range(len(schedules)):
                schedules[i] = schedules[i].loc[self.start_date-pd.Timedelta('1D'):self.date_dictionary_next[schedule_key]]
        else:
            assert False
        return schedules
    
    def compute_PIT_increments(self, schedule_key, expand_dates=False):
        schedules = self.compute_PIT_schedules(schedule_key, 'Goal Period')
        increments = pd.DataFrame([[x.iloc[-1]-x.iloc[0],
                       x.index[1],
                       x.index[-1]] for x in schedules], columns=['Increment', 'Start Date', 'End Date'])
        today = pd.to_datetime(datetime.now().date())
        start = increments['Start Date'] - pd.Timedelta('1D')
        end = increments['End Date'].apply(lambda x: min(x, today))
        increments['Progress'] = self.progress_log.loc[end].values - self.progress_log.loc[start].values
        increments['Completed'] = abs(increments['Progress']) >= abs(increments['Increment'])
        schedule = increments
        if expand_dates:
            start = schedule.drop(columns=['End Date']).rename(columns={"Start Date": "Date"})
            if schedule_key == 'Today':
                schedule = start.set_index('Date').sort_index()
            else:
                end = schedule.drop(columns=['Start Date']).rename(columns={"End Date": "Date"})
                schedule = pd.concat([start, end]).set_index('Date').sort_index()
            
            schedule = schedule.reindex(index=pd.date_range(schedule.index[0], schedule.index[-1]))
            schedule = schedule.fillna(method='ffill')
        return schedule
    
    def compute_streak(self, schedule_key):
        streak_data = self.compute_PIT_schedules(schedule_key, "Overlap")
        streak_data = streak_data[:-1]
        streak_data_progress = pd.concat([x.iloc[-1:] for x in streak_data]).to_frame()
        streak_data_progress.columns = ['Expected Progress']
        
        actual_progress = pd.concat([self.progress_log.loc[x.index[-1]:x.index[-1]] for x in streak_data]).to_frame()
        actual_progress.columns = ['Actual Progress']
        
        streak_data_ex_work = pd.concat([x.iloc[-1:] - x.iloc[0] for x in streak_data]).to_frame()
        streak_data_ex_work.columns = ['Expected Work Done']
        
        actual_work_done = pd.concat([self.progress_log.loc[x.index[-1]:x.index[-1]] - self.progress_log.loc[x.index[0]] for x in streak_data]).to_frame()
        actual_work_done.columns = ['Actual Work Done']
        
        streak_data = pd.concat([streak_data_progress, actual_progress, streak_data_ex_work, actual_work_done], axis=1)
        streak = (abs(streak_data['Actual Work Done']) >= abs(streak_data['Expected Work Done'])).astype(int)
        streak = streak.iloc[::-1].cumprod().sum()
        return streak_data, streak


        