import settings
from redmine_pydal import get_db
import locale

locale.setlocale(locale.LC_NUMERIC,"rus")

db = get_db()

def list_child_issues_without_estimate_on_current_milestone():
    in_current_milestone = db.issues.fixed_version_id == settings.current_milestone
    has_parent_set = db.issues.parent_id != None
    closed = db.issues.status_id.belongs(settings.statuses_closed)
    no_estimate = (db.issues.estimated_hours == None) | (db.issues.estimated_hours < .01)
    not_done = db.issues.status_id.belongs(settings.statuses_not_done)

    query = ~closed & in_current_milestone & has_parent_set & no_estimate & not_done

    #print db(query)._select()
    rows = db(query).select()
    for row in rows:
        print row.id, row.assigned_to_id.lastname, row.subject, row.status_id.name

def get_direct_children_of_an_issue(issue):
    query = db.issues.parent_id == issue
    rows = db(query).select()
    return set(map(lambda r: r.id, rows))

def get_items_by_query(query):
    rows = db(query).select()
    return map(lambda r: r.id, rows)

def get_items_with_children(items, table):
    prev_items = set()
    while (items-prev_items>set()):
        children = set(get_items_by_query(table.parent_id.belongs(items)))
        prev_items = items.copy()
        items|=children
    return items

def get_hours_spent_on_issue(issue):
    query = (db.time_entries.entity_type == 'Issue') & (db.time_entries.entity_id == issue)
    sum = db.time_entries.hours.sum()
    return db(query).select(sum).first()[sum]

def get_hours_spent_on_issue_with_children(issue):
    hours = 0
    for issue in get_items_with_children({issue}, db.issues):
        issue_hours = get_hours_spent_on_issue(issue)
        if issue_hours is not None: 
            hours += issue_hours
    return hours

issue = 22099

hours = []
hours.append((issue, get_hours_spent_on_issue(issue)))

for issue in get_direct_children_of_an_issue(issue):
    hours.append((issue, get_hours_spent_on_issue_with_children(issue)))

total = 0

for (issue, hrs) in hours:
    total += hrs
    print "{}\t{}\t{}".format(issue, db.issues(issue).subject, locale.str(hrs))

print "Total\t{}".format(total)

