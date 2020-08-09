import pandas as pd

class Group:
    
    def __init__(self, data):
        self.data = data
        
    def build_group_schedule(self, key, data_type='Basic'):
        schedules = self.data['Object'].apply(lambda x: x.schedules[key]).transpose()
        schedules.columns = self.data['Goal Name']
        if data_type == 'Basic':
            return schedules
        elif data_type == 'Completion':
            expected_progress = schedules.copy()
            start = expected_progress.apply(lambda x: x.loc[x.first_valid_index()])
            expected_progress = expected_progress.subtract(start).iloc[1:].stack()
            schedules = schedules.iloc[1:].stack()
            schedules = pd.concat([schedules, expected_progress], axis=1)
            schedules.columns = ['Progress', 'Work Required']
            schedules.index.names = ['Date', 'Goal Name']
            temp = self.data.set_index('Goal Name')['Object'].apply(lambda x: x.current_progress)
            temp.name = "Current Progress"
            temp2 = temp - start
            temp2.name = "Work Done"
            schedules = schedules.join(temp, on=["Goal Name"])
            schedules = schedules.join(temp2, on=["Goal Name"])
            schedules['Completed'] = abs(schedules['Work Done']) > abs(schedules['Work Required'])
            schedules = schedules.reset_index()
            return schedules
        else:
            assert False