from redmine_mysql import * 
from redmine_rest import easyRedmineWrapper
import settings
from utils import get_issues_from_command_line

issues = get_issues_from_command_line()

issues = get_not_closed_issues_with_children(issues)

# returns list of tuples (issue, project, status)
issue_collection = get_issues_with_projects_and_statuses(issues)

erw = easyRedmineWrapper()

for (issue,project,status) in issue_collection:
   person = settings.responsible_for_project[project] if project in settings.responsible_for_project else settings.responsible_for_project['*']
   print issue, project, status, person 
   if status in settings.statuses_ready_for_deploy:
       erw.set_issues_status_and_assigned(issue, settings.statuses['production_deployed'], person); 
   elif status in settings.non_blocking_statuses_for_issues:
       print "Issue {0} already has 'deployed' status".format(issue)
   else:
       raise "Not allowed status for deployment: {0} of issue {1}".format(status, issue)
       