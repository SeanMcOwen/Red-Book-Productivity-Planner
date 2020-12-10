import pandas as pd
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

def create_progress_log2(progress_log, frequency):
    progress_log = progress_log.copy()
    if frequency == 'Daily':
        return progress_log
    elif frequency == 'Weekly':
        progress_log = progress_log.groupby([progress_log.index.year, progress_log.index.week]).sum()
        return progress_log
    elif frequency == "Monthly":
        progress_log = progress_log.groupby([progress_log.index.year, progress_log.index.month]).sum()
        return progress_log
    elif frequency == "Quarterly":
        progress_log = progress_log.groupby([progress_log.index.year, progress_log.index.quarter]).sum()
        return progress_log
    elif frequency == "Yearly":
        progress_log = progress_log.groupby(progress_log.index.year).sum()
        return progress_log
    else:
        assert False
        
def create_progress_log3(progress_log, progress_log2, frequency):
    progress_log = progress_log.copy()
    if frequency == 'Daily':
        return progress_log
    elif frequency == 'Weekly':
        progress_log.iloc[:] = progress_log2.loc[pd.MultiIndex.from_tuples(list(zip(*[progress_log.index.year, progress_log.index.week])))].values
        return progress_log
    elif frequency == "Monthly":
        progress_log.iloc[:] = progress_log2.loc[pd.MultiIndex.from_tuples(list(zip(*[progress_log.index.year, progress_log.index.month])))].values
        return progress_log
    elif frequency == "Quarterly":
        progress_log.iloc[:] = progress_log2.loc[pd.MultiIndex.from_tuples(list(zip(*[progress_log.index.year, progress_log.index.quarter])))].values
        return progress_log
    elif frequency == "Yearly":
        progress_log.iloc[:] = progress_log2.loc[progress_log.index.year].values
        return progress_log
    else:
        assert False


class Habit:
    def __init__(self, habit_params, progress_log):
        self.habit_name = habit_params['Habit Name']
        self.group = habit_params['Group']
        self.start_date = habit_params['Start Date']
        self.units = habit_params['Units']
        self.frequency = habit_params['Frequency']
        self.progress_log = progress_log
        
        self.progress_log = self.progress_log.reindex(index=pd.date_range(self.start_date,
                                                                          pd.to_datetime(datetime.now().date())))
        self.progress_log = self.progress_log.fillna(0)
        
        self.progress_log2 = create_progress_log2(self.progress_log, self.frequency)
        self.progress_log3 = create_progress_log3(self.progress_log, self.progress_log2, self.frequency)
        
        self.streak = (self.progress_log2.iloc[:-1][::-1] >= self.units).astype(int).cumprod().sum()
        if len(self.progress_log2) == 0:
            self.completion_percent = np.NaN
        else:
            self.completion_percent = (self.progress_log2 >= self.units).mean()
        
        