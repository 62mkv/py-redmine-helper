import settings
from redmine_pydal import get_db

db = get_db()

in_current_milestone = db.issues.fixed_version_id == settings.current_milestone
has_parent = ~(db.issues.parent_id == None)
closed = db.issues.status_id.belongs(settings.statuses_closed)
no_estimate = (db.issues.estimated_hours == None) | (db.issues.estimated_hours < .01)
not_done = db.issues.status_id.belongs(settings.statuses_not_done)

query = ~closed & in_current_milestone & has_parent & no_estimate & not_done

print db(query)._select()
rows = db(query).select()
for row in rows:
    print row.id, row.assigned_to_id.lastname, row.subject, row.status_id.name