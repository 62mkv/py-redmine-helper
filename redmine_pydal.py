from sshtunnel import SSHTunnelForwarder
import settings
from pydal import DAL, Field

def dal_connect():
    server = SSHTunnelForwarder(
             (settings.ssh_host, settings.ssh_port),
             ssh_password=settings.ssh_password,
             ssh_username=settings.ssh_username,
             remote_bind_address=('127.0.0.1', 3306))

    server.start()

    uri = 'mysql://{username}:{password}@127.0.0.1:{port}/{db}'.format(
           username = settings.mysql_username,
           password = settings.mysql_password,
           db = settings.mysql_dbname,
           port = server.local_bind_port
        )

    db = DAL(uri, migrate = False)
    return db


def get_db():
    db = dal_connect()
    db.define_table('users',Field('firstname'),Field('lastname'))
    db.define_table('statuses',Field('name'), rname='issue_statuses')
    db.define_table('issues',
         Field('subject'),
         Field('parent_id'),
         Field('fixed_version_id'),
         Field('status_id', 'reference statuses'),
         Field('estimated_hours','float'),
         Field('assigned_to_id','reference users')
        )
    db.define_table('time_entries',
         Field('user_id', 'reference users'),
         Field('hours'),
         Field('entity_type'),
         Field('entity_id')
        )

    return db
