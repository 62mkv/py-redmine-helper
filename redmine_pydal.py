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

    print "Creating db"
    db = DAL(uri, migrate = False)
    print "Created db"
    return db