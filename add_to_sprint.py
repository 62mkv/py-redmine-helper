#!/usr/bin/python
from redmine_rest import easyRedmineWrapper
from redmine_mysql import get_not_closed_issues_with_children
from utils import get_issues_from_command_line
import settings

erw = easyRedmineWrapper(settings.redmine_api_key)
issues = get_issues_from_command_line()
issues = get_not_closed_issues_with_children(issues)
erw.add_issues_on_sprint(issues, 5, "Milestone 1 Final")
