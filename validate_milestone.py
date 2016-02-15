from redmine_mysql import *
from redmine_rest import erw
import settings
import query as queries

def validate_sprint():
    # identifying orphaned issues on Current Milestone not on "New development" (there should NOT be such issues)
    query=queries.select_issues_without_parents_on_milestone_X_not_on_project_Y.format(fixed_version_id=settings.current_milestone, project_id=60)
    issues = get_items_by_query(query)
    if (len(issues)>0):
       print "This issues should not be orphans!"
       print issues
       exit(1)

    query = queries.select_open_issues_on_current_milestone_not_on_any_sprint.format(
           milestone_id = settings.current_milestone, closed_statuses = ', '.join(map(str,settings.statuses_closed)))

    issues = get_items_by_query(query)

    issues = get_not_closed_issues_with_children(issues)

    print "Processing issues: "
    print issues
    sprints = get_sprints()
    if sprints.get(settings.current_sprint) is not None:
        erw.add_issues_on_sprint(issues, settings.current_sprint, sprints[settings.current_sprint])


def validate_milestone():
    project_id = settings.main_project 
    # build list of issues without parent on milestone

    milestones = get_open_milestones_for_project(project_id)
    issues = set()
    for ms in milestones.keys():
        issues |= get_issues_without_parent_on_milestone(ms)

    # get list of all children for each task 
    issues_with_children = get_issues_with_children(issues)

    # get milestones for each issue, incuding children
    milestones_of_children = get_milestones_for_issues(issues_with_children)
    # returns dict of { issue_id: milestone_id} 

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

validate_milestone()
validate_sprint()
