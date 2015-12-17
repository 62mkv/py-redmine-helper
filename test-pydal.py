import settings
from redmine_pydal import dal_connect
from pydal import Field

db = dal_connect()
db.define_table('users',Field('firstname'),Field('lastname'))
db.users.name = Field.Virtual('name', lambda r:r['firstname'][0]+' '+r['lastname'])
db.define_table('statuses',Field('name'), rname='issue_statuses')
db.define_table('issues',
     Field('subject'),
     Field('parent_id'),
     Field('fixed_version_id'),
     Field('status_id', 'reference statuses'),
     Field('estimated_hours','float'),
     Field('assigned_to_id','reference users')
    )
in_current_milestone = db.issues.fixed_version_id == settings.current_milestone
has_parent = ~(db.issues.parent_id == None)
closed = db.issues.status_id.belongs(5,7)
no_estimate = (db.issues.estimated_hours == None) | (db.issues.estimated_hours < .01)
not_done = db.issues.status_id.belongs(settings.statuses_not_done)

query = ~closed & in_current_milestone & has_parent & no_estimate & not_done

print db(query)._select()
rows = db(query).select()
for row in rows:
    print row.id, row.assigned_to_id.lastname, row.subject, row.status_id.name