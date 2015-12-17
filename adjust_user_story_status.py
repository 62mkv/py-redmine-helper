from redmine_mysql import get_statuses_for_issues, get_children_of_issue, issue_has_children
from redmine_rest import erw
from utils import get_issues_from_command_line

status_priority = {
 13: 0 # И Обсуждение = Обсуждение
 ,2:  1 # И В работе = В работе
 ,14: 2 # Требует доработки = В работе
 ,1:  3 # Новая
 ,3:  4 # Решена
 ,9:  5 # Проверена на тестовом
 ,5:  6 # Закрыта
}

def adjust_status_from_children(issue, status):
    current_status = 5 #status 
    children = get_children_of_issue(issue)
    statuses = get_statuses_for_issues(children)
    for child in children:
        if issue_has_children(child):
            status = adjust_status_from_children(child, statuses[child])
            if status != statuses[child]:
                erw.set_issues_status(child, status) 
        else:
            status = statuses[child]
        if status_priority.get(status) is not None and status_priority.get(current_status) is not None:
            if status_priority[status] < status_priority[current_status]:
                current_status = status
    return current_status 
 
issues = get_issues_from_command_line

statuses_for_issues = get_statuses_for_issues(issues)

for issue in issues:
    status = adjust_status_from_children(issue, statuses_for_issues[issue])
    if status != statuses_for_issues[issue]:
        erw.set_issues_status(issue, status)
        