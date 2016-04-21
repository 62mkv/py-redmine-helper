import json
from datetime import date
from redmine_instances import rminstances

def print_my_time_today():
    time_entries = list()
    today = date.today()

    def add_to_list(_time_entries, r):
        for te in _time_entries:
            time_entries.append((r, te['spent_on'], te['hours'], te['comments'], te['created_on']))

    def add_time_entries(rw, label, user_id, projects):
        for project in projects: 
            resp = json.loads(rw.get_time_entries([('project_id', project), ('user_id', user_id),('limit', 100)]))
            add_to_list(resp["time_entries"], label)

    for rminstance in rminstances:
        add_time_entries(rminstance[0], rminstance[1], rminstance[2].my_user_id, rminstance[2].projects_with_time)

    total = 0 

    time_entries.sort(key=lambda x: x[4])
    for te in time_entries:
        if str(te[1]) == str(today):
            print te[0], te[1], te[2], te[3]#, te[4]
            total += te[2]

    print total

print_my_time_today()

#erw.post_time_entries_with_payload(
#     {'issue_id': 35607, 
#      'hours': 1, 
#      'activity_id': 14,
#      'comments': '11:00 - подготовка тех задания - 12:00'
#      })

