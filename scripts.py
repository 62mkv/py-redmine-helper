from redmine_mysql import get_spent_time_with_subtasks, get_statuses_for_issues, get_statuses, get_filtered_table_as_dict
from datetime import date
from utils import as_in
import settings

def count_time_spent_on_user_story(issues, tilldate = ""):
    statuses_for_issues = get_statuses_for_issues(issues)

    statuses = get_statuses()

    issue_subjects = get_filtered_table_as_dict('id','subject','issues','id in ({0})'.format(as_in(issues)))

    grand_total = 0
    today = date.today().isoformat() #"2015-12-31 23:59:59" 

    for issue in issues:
        bugs_free = 'BUGS FREE' in issue_subjects[issue]
        if tilldate == "": tilldate=today
        (total, spent_line) = get_spent_time_with_subtasks(issue, settings.start_date, tilldate, bugs_free)
        status = statuses[statuses_for_issues[issue]]
        print "{0};{1};{2};{3}".format(issue, str(total), status, spent_line) # .replace(".",",")
        grand_total += total

    print "\nTotal: {0}".format(grand_total)
