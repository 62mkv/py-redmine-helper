#!/usr/bin/python
from redmine_mysql import get_not_closed_issues_with_children, get_cursor_by_query, get_items_by_query, get_projects_with_children, get_issues_with_statuses, test_issue_statuses, get_statuses
from utils import get_issues_from_command_line
import settings

issues = get_issues_from_command_line()

issues = get_not_closed_issues_with_children(issues)

# checking status for issues
issues_in_status = get_issues_with_statuses(issues)

statuses = get_statuses()

errors = test_issue_statuses(issues_in_status, statuses, settings.allowed_statuses_for_testing, "issues")
