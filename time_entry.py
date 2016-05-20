import json
import utils
from datetime import date as _date, timedelta
from rminstance import common
from redmine_instances import rminstances
from collections import namedtuple

TimeEntry = namedtuple('TimeEntry','rminstance,project,issue,spent_on,hours,comment,created_on')

def print_user_time_entries(time_entries, date):
    total = 0 
    time_entries.sort(key=lambda x: x.created_on)
    for te in time_entries:
#        print te
        if str(te.spent_on) == str(date):
            print utils.join_with(te, u'\t')
            total += te.hours

    print total

def show_user_time_entries(user, date):
    time_entries = list()

    def add_to_list(_time_entries, r):
        for te in _time_entries:
            time_entries.append(TimeEntry._make([r, te['project']['name'], te['issue']['id'], te['spent_on'], te['hours'], te['comments'], te['created_on']]))

    def add_time_entries(rw, label, user_id, projects):
        for project in projects: 
            params = [('project_id', project), ('user_id', user_id), ('spent_on', date)]
            add_to_list(rw.get_items_as_json_full('time_entries', params), label)
 
    for rminstance in rminstances:
        add_time_entries(rminstance.rest_wrapper, rminstance.label, rminstance.team.team[user], rminstance.settings.projects_with_time)

    print_user_time_entries(time_entries, date)


def print_team_time_spent_on_date(_date):
    users = set()
    for rminstance in rminstances:
        for user in rminstance.team.team:
              users |= {user}

    for user in users:
        print user
        show_user_time_entries(user, _date)


def print_team_time_spent_last_day():
    return print_team_time_spent_on_date(utils.get_last_working_day())


def print_my_time_spent_today():
    return show_user_time_entries(common.me, _date.today())

#erw.post_time_entries_with_payload(
#     {'issue_id': 35607, 
#      'hours': 1, 
#      'activity_id': 14,
#      'comments': '11:00 - подготовка тех задания - 12:00'
#      })

def load_time_entries(rw, params, function):
    return rw.get_items_as_json_full('time_entries', params, function)
