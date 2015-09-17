#!/usr/bin/python
from redmine_mysql import get_not_closed_issues_with_children, get_cursor_by_query, get_issues_by_query
import settings
import re
import sys
from utils import get_issues_from_command_line

issues = get_issues_from_command_line()

def get_branches_for_issues(issues):
    in_clause = ', '.join(map(str,issues))
    query = "SELECT notes, journalized_id FROM journals WHERE journalized_id IN ("+in_clause+") and journalized_type='Issue' and user_id=156"

    cur = get_cursor_by_query(query)
    branch_list = dict()

    for row in cur.fetchall():
        m=re.search(r"Repo <b>(\S+)</b> branch <b>(\S+)</b>",row[0])
        if m is None:
           continue 
        repo= m.group(1)
        branch = m.group(2)
        key = '\\'.join((repo, branch))
        if key in branch_list:
           branch_list[key].add(row[1])
        else:
           branch_list[key] = set([row[1]])

    return branch_list

def get_issues_with_statuses(issues):
    if len(issues) == 0:
        return dict()
    query="SELECT id, status_id from issues where id in ("+", ".join(map(str, issues))+")"
    cur = get_cursor_by_query(query)
    issues_in_status = dict()
    for row in cur.fetchall():
       if row[1] in issues_in_status:
          issues_in_status[row[1]].append(row[0])
       else:
          issues_in_status[row[1]] = [row[0]]
    return issues_in_status

query = "SELECT id, name FROM issue_statuses"
cur = get_cursor_by_query(query)

statuses = dict()
for row in cur:
  statuses[row[0]] = row[1]

issues = get_not_closed_issues_with_children(issues)

# checking status for issues
issues_in_status = get_issues_with_statuses(issues)

errors = False
for s in issues_in_status.iterkeys():
   if s not in settings.non_blocking_statuses:
       print "ERROR: issues {",', '.join(map(str,issues_in_status[s])),"} are not in allowed status: ",statuses[s].decode('utf8').encode('cp866')
       errors = True

# checking if any blocking issues are not in non-blocking status
query = "SELECT issue_from_id FROM issue_relations WHERE relation_type='blocks' AND issue_to_id IN ("+', '.join(map(str,issues))+")"
blockers = filter(lambda b: b not in issues, get_issues_by_query(query))

blockers_in_status = get_issues_with_statuses(blockers)

for s in blockers_in_status.iterkeys():
   if s not in settings.non_blocking_statuses:
       print "ERROR: blocking issues {",', '.join(map(str,blockers_in_status[s])),"} are not in allowed status: ",statuses[s].decode('utf8').encode('cp866')
       errors = True

if errors:
   print "Deployment is forbidden: see above"
   sys.exit(1)

branches = get_branches_for_issues(issues)

for branch in branches.iterkeys():
   print branch+ ": "+', '.join(map(str,branches[branch]))

