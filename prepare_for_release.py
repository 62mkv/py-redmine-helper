#!/usr/bin/python
from redmine_mysql import *
import subprocess
import settings
import re
import sys
from utils import get_issues_from_command_line

repo_storage = u'C:\\Users\\Марчук\\Documents\\ClickPhone\\Исходники\\clickphone'

def get_remote_branches_for_commit(repo,commit):
    remote_branches = []
    try:
        contains = subprocess.check_output("git --git-dir={0} branch -a --contains {1}".format(repo_storage+'\\'+repo+'\\\.git',commit))
        for line in contains.split():
            mp = re.match('\s*remotes/origin/(\S+)',line)
            if mp is not None:
                remote_branch = mp.group(1)
                remote_branches += [remote_branch]
    finally:
        return remote_branches

def get_branches_for_issues(issues):

    branch_issues = dict()

    def add_branch_to_issue(issue, key, commit = None):
        if key in branch_issues:
           branch_issues[key].add(issue)
        else:
           branch_issues[key] = set([issue])

    def add_repo_branch(issue, repo, branch, commit):
        key = '\\'.join((repo, branch))
        add_branch_to_issue(issue, key, commit)

    in_clause = ', '.join(map(str,issues))
    query = "SELECT notes, journalized_id FROM journals WHERE journalized_id IN ("+in_clause+") and journalized_type='Issue' and user_id={0}". \
        format(settings.git_robot_redmine_id)

    cur = get_cursor_by_query(query)

    for row in cur.fetchall():
        issue = row[1]
        m=re.search(r"Repo <b>(\S+)</b> branch <b>(\S+)</b> commit <b>(\S+)</b>",row[0])
        if m is None:
            m=re.search(r"NOCOMMITOK",row[0])
            if m is None:  
                continue 
            else:
                add_branch_to_issue(issue, "NOT-A-BRANCH")
        else:
            repo = m.group(1)
            branch = m.group(2)
            commit = m.group(3)
        rb = get_remote_branches_for_commit(repo, commit)
        if not "master" in rb:
            add_repo_branch(issue, repo, branch, commit)
        else:
            add_branch_to_issue(issue, "MERGED")

    return branch_issues

issues = get_issues_from_command_line()

statuses = get_statuses()

issues = get_not_closed_issues_with_children(issues)

# checking status for issues
# returns dict { status1: [issue1, ...] }
issues_in_status = get_issues_with_statuses(issues)

# check if some of the issues are already deployed
for status in settings.statuses_deployed:
    if issues_in_status.get(status) is not None:
         print 'Already deployed: {}'.format(', '.join(map(str,issues_in_status[status])))
         issues -= set(issues_in_status[status])
         del issues_in_status[status]

# check if any of the issues are not in allowed status for deployment
errors = test_issue_statuses(issues_in_status, statuses, settings.non_blocking_statuses_for_issues, "issues")

# checking if any blocking issues are not in non-blocking status
query = "SELECT issue_from_id FROM issue_relations WHERE relation_type='blocks' AND issue_to_id IN ("+', '.join(map(str,issues))+")"

# IMPORTANT: here we are only interested in EXTERNAL blockers (from other user stories)
blockers = filter(lambda b: b not in issues, get_items_by_query(query))

blockers_in_status = get_issues_with_statuses(blockers)
errors = test_issue_statuses(blockers_in_status, statuses, settings.non_blocking_statuses_for_blockers, "blockers") or errors

if errors:
   print "Deployment is forbidden: see above"
   sys.exit(1)

branches = get_branches_for_issues(issues)

issues_with_branches = set()

# removing any non-fully merged issue from "MERGED" 'branch':
for branch in branches.keys():
   if branch != "MERGED":
       for issue in branches[branch]:
           if issue in branches["MERGED"]:
               branches["MERGED"].remove(issue)

# printing all the branches and their issues to deploy:
for branch in sorted(branches.keys()):
   print branch+ ": "+', '.join(map(str,branches[branch]))
   issues_with_branches |= branches[branch]

issues_without_branches = issues - issues_with_branches

development_projects = get_projects_with_children({75}) - {60}

if len(issues_without_branches) > 0:
    issues_without_branches_in_development_projects = get_items_by_query("SELECT id from issues WHERE id in ({issue_list}) AND project_id in ({project_list})".format(
        issue_list = ', '.join(map(str,issues_without_branches)), project_list=', '.join(map(str,development_projects))))
    print "The following issues in development projects have no branches mentioned in Redmine updates: "+ ', '.join(map(str,issues_without_branches_in_development_projects))
   
    issues_without_branches_in_new_development = get_items_by_query("SELECT id from issues WHERE id in ({issue_list}) AND project_id in ({project_list})".format(
        issue_list = ', '.join(map(str,issues_without_branches)), project_list=', '.join(map(str,{60}))))

    print "The following issues in new development have no branches mentioned in Redmine updates: "+ ', '.join(map(str,issues_without_branches_in_new_development))
