from redmine_mysql import get_items_by_query, get_issues_with_children, get_cursor_by_query
from redmine_rest import easyRedmineWrapper
import settings

milestones = dict()

def get_issues_without_parent_on_milestone(milestone_id):
    query="SELECT id FROM issues i WHERE i.parent_id is NULL and i.fixed_version_id in ({0})".format(milestone_id)
    return get_items_by_query(query)

def get_issues_without_parent_on_any_milestone_from_project(project_id):
    query="SELECT id, name FROM versions v WHERE v.project_id={} and v.status='open'".format(project_id)
    cur = get_cursor_by_query(query)
    for row in cur.fetchall():
        milestones[row[0]] = row[1]
    issues = set()
    for ms in milestones.keys():
        issues |= get_issues_without_parent_on_milestone(ms)
    return issues

def get_milestones_for_issues(issues):
    query = "SELECT id, fixed_version_id FROM issues WHERE id in ({issue_list})".format(issue_list=', '.join(map(str,issues)))
    cur = get_cursor_by_query(query)
    dict_issue_milestone = dict()
    for row in cur.fetchall():
        dict_issue_milestone[row[0]] = row[1]
    return dict_issue_milestone
   
def get_parents_for_issues(issues):
    query = "SELECT id, parent_id FROM issues WHERE id in ({})".format(','.join(map(str,issues)))
    cur = get_cursor_by_query(query)
    parent_issue = dict()
    for row in cur.fetchall():
        parent_issue[row[0]] = row[1]
    return parent_issue

def get_roots_for_issues(issues):
    parents = get_parents_for_issues(issues)
    counter = 1
    while counter>0:
        counter = 0
        for issue in parents.keys():
            if parents.get(parents[issue]) is not None:
                 parents[issue] = parents[parents[issue]]
                 counter += 1
    return parents

project_id = settings.main_project 
# build list of issues without parent on milestone

issues = get_issues_without_parent_on_any_milestone_from_project(project_id)

# get list of all children for each task 
issues_with_children = get_issues_with_children(issues)

# get milestones for each issue, incuding children
milestones_of_children = get_milestones_for_issues(issues_with_children)
# returns dict of { issue_id: milestone_id} 

erw = easyRedmineWrapper()

# for every issue that is not on a necessary milestone, we adjust milestone
issues_to_add = dict()
for ms in milestones.keys():
    issues_to_add[ms] = set()

issue_roots = get_roots_for_issues(issues_with_children)

for issue in issues_with_children:
    issue_parent = issue_roots[issue]
    if issue_parent is not None:
       if milestones_of_children[issue] != milestones_of_children[issue_parent]:
           issues_to_add[milestones_of_children[issue_parent]] |= {issue}

for ms in milestones.keys():
    if len(issues_to_add[ms])>0:
        for issue in issues_to_add[ms]:
            print "Adding {0} to milestone {1}".format(issue, milestones[ms])
        erw.add_issues_to_milestone(issues_to_add[ms], ms, milestones[ms])

