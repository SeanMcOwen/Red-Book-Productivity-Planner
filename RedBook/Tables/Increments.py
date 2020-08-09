import pandas as pd

def build_expected_progress_table(goals):
    increments = goals.set_index('Goal Name')['Object'].apply(lambda x: pd.Series(x.schedule_goals))
    temp = goals.set_index('Goal Name')['Object'].apply(lambda x: x.current_progress)
    temp.name = "Current"
    increments = pd.concat([temp,increments], axis=1)
    return increments

def build_expected_work_table(goals):
    increments = goals.set_index('Goal Name')['Object'].apply(lambda x: pd.Series(x.increments))
    return increments

def build_percent_left_table(goals):
    increments = goals.set_index('Goal Name')['Object'].apply(lambda x: pd.Series(x.increments_percent))
    return increments


def build_expected_work_tables(goals):
    expected_progress_table = build_expected_progress_table(goals)
    expected_work_table = build_expected_work_table(goals)
    percent_left_table = build_percent_left_table(goals)
    
    expected_work_tables = {}
    for key in expected_work_table.keys():
        expected_work_tables[key] = pd.concat([expected_progress_table['Current'],
                                              expected_progress_table[key],
                                              expected_work_table[key],
                                              percent_left_table[key]], axis=1)
        expected_work_tables[key].columns = ['Current', 'Goal Progress', 'Progress Left', 'Percent Left']
    return expected_progress_table, expected_work_table, percent_left_table, expected_work_tables

def build_effective_date_table(goals):
    effective_dates = goals.set_index('Goal Name')['Object'].apply(lambda x: pd.Series(x.effective_schedule_dates))
    return effective_dates


def build_expected_work_tables_today(goals):
    current = goals.set_index('Goal Name')['Object'].apply(lambda x: x.current_progress)
    schedule_goals = goals.set_index('Goal Name')['Object'].apply(lambda x: pd.Series(x.schedule_goals_today))
    increments = goals.set_index('Goal Name')['Object'].apply(lambda x: pd.Series(x.increments_today))
    effective_dates = build_effective_date_table(goals)
    
    expected_work_tables = {}
    for key in effective_dates.keys():
        expected_work_tables[key] = pd.concat([current,
                                              schedule_goals[key],
                                              increments[key],
                                              effective_dates[key]], axis=1)
        expected_work_tables[key].columns = ['Current', 'Goal Progress', 'Progress Left', 'Effective Date']
    return expected_work_tables
    
    
    