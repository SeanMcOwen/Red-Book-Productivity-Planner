import pandas as pd

    
def build_expected_progress_table_habits(habits):
    table = habits[['Habit Name', 'Frequency']].copy()
    table['Current Progress'] = habits['Object'].apply(lambda x: x.progress_log2.iloc[-1])
    table['Expected Progress'] = habits['Units']
    table['Progress Left'] = table['Expected Progress'] - table['Current Progress']
    return table
