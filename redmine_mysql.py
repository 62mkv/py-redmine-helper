import logging
import MySQLdb
from sshtunnel import SSHTunnelForwarder
import settings

logger = None
server = None
con = None

def get_mysql_connection():
    return SSHTunnelForwarder(
         (settings.ssh_host, settings.ssh_port),
         ssh_password=settings.ssh_password,
         ssh_username=settings.ssh_username,
         remote_bind_address=('127.0.0.1', 3306))

def get_cursor_by_query(query):
    def init_connection():
        global con
        global server
        global logger 
        if con is None:
           logger = logging.getLogger('{}.mysqltest'.format(__name__))
           logger.debug('Starting tunnel')
           server = get_mysql_connection()
           server.start()
           con = None
           logger.debug("Connect to db")
           con = MySQLdb.connect(user=settings.mysql_username,passwd=settings.mysql_password,db=settings.mysql_dbname,host='127.0.0.1',port=server.local_bind_port)
        return con

    cur =  init_connection().cursor()
    cur.execute(query)
    return cur

def get_issues_by_query(query):
    ''' query should return issue "id" as a first column '''
    result = set()
    cur = get_cursor_by_query(query)
    for row in cur.fetchall():
       result.add(row[0])
    return result
    
def get_not_closed_issues_with_children(issues):
    prev_issues = set()
    while (issues-prev_issues>set()):
        issue_list = ', '.join(map(str,issues))
        children = get_issues_by_query("SELECT id FROM issues where parent_id in ("+issue_list+") and status_id not in (5,7)")
        prev_issues = issues.copy()
        issues|=children
    return issues
