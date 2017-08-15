import json
from datetime import datetime, timedelta
from redmine_rest import erw
from utils import get_issues_from_command_line_as_list

def parse_datetime(s):
    return datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ')

statuses = json.loads(erw.get_issue_statuses([]))['issue_statuses']

statuses_dict = dict()

for s in statuses:
    statuses_dict[s['id']] = s['name']

def process_issue(issue):

    print "Processing issue: %d" % issue

    resp = erw.get_item_as_json("issues", issue, [ ('include', 'journals')])

    issue = json.loads(resp)['issue']

    journals = issue['journals']
    created_on = issue['created_on']
    current_status = issue['status']['id']

    history = [ (i['created_on'], i['details'], i['user']) for i in journals]

    filtered = []
    for h in history:
        for d in h[1]:
            if d['property'] == 'attr' and d['name'] == 'status_id':
                filtered += [(h[0], d, h[2])]

    filtered.sort(key=lambda x: x[0])

    status_change_history = []

    previous = created_on
    for (created, details, user) in filtered:
        status_from = int(details['old_value']) # statuses_dict[int(details['old_value'])]
        time_from = previous
        time_to = created
        duration = parse_datetime(time_to) - parse_datetime(time_from)
        status_change_history.append((time_from, time_to, status_from, duration, user['name']))
        previous = time_to

    time_to = datetime.now()
    duration = time_to - parse_datetime(time_from)
    status_change_history.append((time_from, time_to, current_status, duration, ''))

    for s in status_change_history:
        print u"\tSince {} till {}: {}, duration: {} (by {})".format(s[0], s[1], statuses_dict[s[2]], s[3], s[4])

    counters = dict()
    for s in status_change_history:
        if counters.get(s[2]) is None:
            counters[s[2]] = s[3]
        else:
            counters[s[2]] += s[3]

    for (status, duration) in counters.items():
        print '\t%s: %s' % (statuses_dict[status], duration)

issues = get_issues_from_command_line_as_list()
for i in issues: 
    process_issue(i)
