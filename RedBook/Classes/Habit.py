import pandas as pd
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

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