#!/usr/bin/python
from redmine_rest import add_issues_on_sprint
from redmine_mysql import get_not_closed_issues_with_children
from utils import get_issues_from_command_line

issues = get_issues_from_command_line()
issues = get_not_closed_issues_with_children(issues)
add_issues_on_sprint(issues, 5, "Milestone 1 Final")
