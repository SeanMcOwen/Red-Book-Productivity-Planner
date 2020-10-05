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
        
        self.streak = (self.progress_log2.iloc[:-1][::-1] >= self.units).astype(int).cumprod().sum()