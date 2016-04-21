import json
from datetime import date
from redmine_instances import rminstances
from collections import namedtuple

TimeEntry = namedtuple('TimeEntry','rminstance,spent_on,hours,comment,created_on')

def print_my_time_today():
    time_entries = list()
    today = date.today()

    def add_to_list(_time_entries, r):
        for te in _time_entries:
            time_entries.append(TimeEntry._make([r, te['spent_on'], te['hours'], te['comments'], te['created_on']]))

    def add_time_entries(rw, label, user_id, projects):
        for project in projects: 
            resp = json.loads(rw.get_time_entries([('project_id', project), ('user_id', user_id),('limit', 100)]))
            add_to_list(resp["time_entries"], label)

    for rminstance in rminstances:
        add_time_entries(rminstance.rest_wrapper, rminstance.label, rminstance.settings.my_user_id, rminstance.settings.projects_with_time)

    total = 0 

    time_entries.sort(key=lambda x: x.created_on)
    for te in time_entries:
        if str(te.spent_on) == str(today):
#            print te
            print te.rminstance, te.spent_on, te.hours, te.comment#, te[4]
            total += te.hours

    print total

print_my_time_today()

#erw.post_time_entries_with_payload(
#     {'issue_id': 35607, 
#      'hours': 1, 
#      'activity_id': 14,
#      'comments': '11:00 - подготовка тех задания - 12:00'
#      })

