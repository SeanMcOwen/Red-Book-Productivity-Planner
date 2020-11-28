import pandas as pd

    
def build_expected_progress_table_habits(habits):
    table = habits[['Habit Name', 'Frequency']].copy()
    table['Current Progress'] = habits['Object'].apply(lambda x: x.progress_log2.iloc[-1])
    table['Expected Progress'] = habits['Units']
    table['Progress Left'] = table['Expected Progress'] - table['Current Progress']
    return table

def create_streak_tables(habits):
    tables = {}
    for col in ["Daily","Weekly","Monthly","Quarterly","Yearly"]:
        temp = habits[habits['Frequency'] == col].copy()
        
        if len(temp) > 0:
            temp['Streak'] = temp['Object'].apply(lambda x: x.streak)
            temp = temp[['Habit Name', 'Streak']]
            tables[col] = temp
    return tables