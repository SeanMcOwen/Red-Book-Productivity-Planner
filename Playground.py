import RedBook
import pandas as pd
import sqlite3
from datetime import datetime


database_name = 'Goals.db'



def minimum_effective_date(goals, days_behind):
    min_date = goals['Object'].apply(lambda x: min(x.effective_schedule_dates.values()))
    lag = (pd.to_datetime(datetime.now().date()) - min_date).dt.days
    return lag >= days_behind

def effective_date(goals, days_behind, schedule):
    min_date = goals['Object'].apply(lambda x: x.effective_schedule_dates[schedule])
    lag = (pd.to_datetime(datetime.now().date()) - min_date).dt.days
    return lag >= days_behind

def effective_date_top_n(goals, top_n, schedule):
    ed = goals['Object'].apply(lambda x: x.effective_schedule_dates[schedule])
    top_n = ed.sort_values().head(top_n).index
    return pd.Series(goals.index.isin(top_n), index=goals.index)
    

#Percent Complete habit
def habit_completion(habits, completion):
    
    return habits['Object'].apply(lambda x: x.completion_percent) <= completion


def habit_streak(habits, streak):
    return habits['Object'].apply(lambda x: x.streak) <= streak


def and_connector(data, rules):
    out = [rule.apply_rule(data) for rule in rules]
    out = pd.concat(out, axis=1)
    return out.all(axis=1)

def or_connector(data, rules):
    out = [rule.apply_rule(data) for rule in rules]
    out = pd.concat(out, axis=1)
    return out.any(axis=1)

def goal_increment_completed(goals, schedule):
    schedules = goals['Object'].apply(lambda x: x.increments[schedule])
    return ~pd.isnull(schedules)
    
def goal_increment_completed_today(goals, schedule):
    schedules = goals['Object'].apply(lambda x: x.increments_today[schedule])
    return ~pd.isnull(schedules)

def group_check(data, group):
    return data['Group'] == group

class GoalRule:
    def __init__(self, rule_name, args):
        if rule_name == "MED":
            self.rule = minimum_effective_date
        elif rule_name == "ED":
            self.rule = effective_date
        elif rule_name == "AND":
            self.rule = and_connector
        elif rule_name == "OR":
            self.rule = or_connector
        elif rule_name == "GIC":
            self.rule = goal_increment_completed
        elif rule_name == "GICT":
            self.rule = goal_increment_completed_today
        elif rule_name == "GRP":
            self.rule = group_check
        else:
            assert False
        self.args = args
    
    def apply_rule(self, goals):
        return self.rule(goals, *self.args)

class HabitRule:
    def __init__(self, rule_name, args):
        if rule_name == "HC":
            self.rule = habit_completion
        elif rule_name == "HS":
            self.rule = habit_streak
        elif rule_name == "AND":
            self.rule = and_connector
        elif rule_name == "OR":
            self.rule = or_connector
        elif rule_name == "GRP":
            self.rule = group_check
        else:
            assert False
        self.args = args
    def apply_rule(self, habits):
        return self.rule(habits, *self.args)

#Completed for this period

#Pick frequency

#Make one example where it is < x % complete with it not being complete this week

#Add a group select 

def find_arguments(rule):
    if rule['Rule Type'] == "MED":
        return list(rule[['N Days']].values)
    elif rule['Rule Type'] == "ED":
        return list(rule[['N Days', 'Schedule']].values)
    elif rule['Rule Type'] == "GIC":
        return list(rule[['Schedule']].values)
    elif rule['Rule Type'] == "GICT":
        return list(rule[['Schedule']].values)        
    else:
        assert False

from datetime import datetime
with sqlite3.connect(database_name) as conn:
    #existing_progress = list(pd.read_sql("SELECT * FROM progress", conn)['Goal Name'].unique())
    #goals, work_log = RedBook.Data.process_goals_SQL(conn)
    #expected_progress_table, expected_work_table, percent_left_table, expected_work_tables = RedBook.Tables.build_expected_work_tables(goals)
    #RedBook.Data.filter_increment_hiding(goals, expected_work_tables)
    #print(RedBook.Data.check_table_exists(conn, 'groups'))
    #tables 
    
    
    goals, work_log = RedBook.Data.process_goals_SQL(conn)
    goal_rules = pd.read_sql("SELECT * FROM rules", conn)
    goal_rules['Object'] = goal_rules[~goal_rules['Rule Type'].isin(['AND', 'OR'])].apply(lambda rule: GoalRule(rule['Rule Type'], find_arguments(rule)), axis=1)
    goal_rules = goal_rules.set_index('Rule Name')
    for rule_name in goal_rules.index:
        if goal_rules.loc[rule_name, 'Rule Type'] in ['AND', 'OR']:
            args = list(goal_rules.loc[goal_rules.loc[rule_name][['Rule 1', 'Rule 2']].values]['Object'].values)
            rtype = goal_rules.loc[rule_name, 'Rule Type']
            goal_rules.loc[rule_name, 'Object'] = GoalRule(rtype, args)
    
    """    
    habits, progress = RedBook.Data.process_habits_SQL(conn)
    
    r1 = HabitRule("HC", [.1])
    r2 = HabitRule("GRP", ['Leisure'])
    r3 = HabitRule("AND", [[r1, r2]])
    print(r3.apply_rule(habits))
    """
    #print(goal_increment_completed(goals, "Quarter"))
    #print(goal_increment_completed_today(goals, "Quarter"))
    #expected_progress_table = RedBook.Tables.build_expected_progress_table(goals)
    #expected_work_table = RedBook.Tables.build_expected_work_table(goals)
    
    #expected_progress_table, expected_work_table, expected_work_tables = RedBook.Tables.build_expected_work_tables(goals)

    
    #habits, progress = RedBook.Data.process_habits_SQL(conn)
    #a = RedBook.Tables.create_streak_tables(habits)
    #print(a)

    #print(pd.to_datetime(pl.index.get_level_values(0).astype(str), format='%Y') + \
    #         pd.to_timedelta((pl.index.get_level_values(1) * 7).astype(str) + ' days'))
    #print(create_progress_log3(a.progress_log2, "Weekly"))
    #table = RedBook.Tables.build_expected_progress_table_habits(habits)
    #["Daily","Weekly","Monthly","Quarterly","Yearly"]
    #tasks = RedBook.Data.pull_tasks_SQL(conn)

    #RedBook.Data.check_goal_completion(conn, goals)
    #tasks = RedBook.Data.pull_tasks_SQL(conn)
    