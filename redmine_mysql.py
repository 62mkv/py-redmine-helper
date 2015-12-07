import logging
import MySQLdb
import MySQLdb.cursors
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

def get_cursor_by_query(query, cursorclass = MySQLdb.cursors.Cursor):
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
           con = MySQLdb.connect(
               user=settings.mysql_username,
               passwd=settings.mysql_password,
               db=settings.mysql_dbname,
               host='127.0.0.1',
               port=server.local_bind_port,
               cursorclass= cursorclass)
        return con

    cur =  init_connection().cursor()
    cur.execute(query)
    return cur

def get_items_by_query(query):
    ''' query should return item "id" as a first column '''
    result = set()
    cur = get_cursor_by_query(query)
    for row in cur.fetchall():
       result.add(row[0])
    return result

def get_items_with_children(items, table, keyname, parent_key_name, where=""):
    prev_items = set()
    while (items-prev_items>set()):
        item_list = ', '.join(map(str,items))
        children = get_items_by_query("SELECT {key} FROM {table} where {parent_key_name} in (".format(key=keyname,table=table,parent_key_name=parent_key_name)+item_list+") "+ where)
        prev_items = items.copy()
        items|=children
    return items

def get_issues_with_children(issues, where=""):
    return get_items_with_children(issues, 'issues', 'id', 'parent_id', where)

def get_not_closed_issues_with_children(issues):
    return get_issues_with_children(issues, " and status_id not in (5,7)")

def get_projects_with_children(projects, where=""):
    return get_items_with_children(projects, 'projects', 'id','parent_id', where)

def get_spent_time_with_subtasks(issue, start_date, end_date):
    query = """
    SELECT ROUND(SUM(hours),2), u.lastname, gu.group_id  FROM time_entries te
      JOIN users u ON te.user_id = u.id
      LEFT OUTER JOIN groups_users gu ON te.user_id = gu.user_id
      WHERE te.entity_type='Issue'  AND te.spent_on BETWEEN '{start_date}' AND '{end_date}'
         AND te.entity_id IN ({issue_list}) 
         AND gu.group_id IN (130,162)
      GROUP BY u.lastname, gu.group_id
    """.format(start_date=start_date, end_date=end_date,issue_list=", ".join(map(str,get_issues_with_children(set([issue])))))
                                      
    cur = get_cursor_by_query(query)

    total = 0
    spent_details = ''
    for row in cur.fetchall():
       hrs = float(row[0])
       lastname = row[1]
       spent_details += lastname.decode('utf8').encode('cp866') + ': '+str(hrs)+', '
       total += hrs

    return total,spent_details

def get_issues_with_statuses(issues):
    if len(issues) == 0:
        return dict()
    query="SELECT id, status_id from issues where id in ("+", ".join(map(str, issues))+")"
    cur = get_cursor_by_query(query)
    issues_in_status = dict()
    for row in cur.fetchall():
       if row[1] in issues_in_status:
          issues_in_status[row[1]].append(row[0])
       else:
          issues_in_status[row[1]] = [row[0]]
    return issues_in_status

def get_statuses_for_issues(issues):
    issues_in_status = get_issues_with_statuses(issues)
    statuses_for_issues = dict()
    for status in issues_in_status.keys():
        for issue in issues_in_status[status]:
            statuses_for_issues[issue] = status
    return statuses_for_issues
  
def get_issues_with_projects_and_statuses(issues):
    if len(issues) == 0:
        return []
    query="SELECT id, project_id, status_id from issues where id in ({0})".format(", ".join(map(str, issues)))
    cur = get_cursor_by_query(query)
    res = []
    for row in cur.fetchall():
       res.append((row[0],row[1],row[2]))

    return res

def test_issue_statuses(issues, statuses, allowed_statuses, issue_description):
   flag = False
   for s in issues.iterkeys():
      if s not in allowed_statuses:
          print "ERROR: ",issue_description," {",', '.join(map(str,issues[s])),"} are not in allowed status: ",statuses[s]
          flag = True
   return flag

def get_statuses():
    query = "SELECT id, name FROM issue_statuses"
    cur = get_cursor_by_query(query)

    statuses = dict()
    for row in cur:
      statuses[row[0]] = row[1].decode('utf8').encode('cp866')
    return statuses

def get_children_of_issue(issue):
    return get_issues_with_children(set([issue])) - set([issue])

def issue_has_children(issue):
    cur = get_cursor_by_query("SELECT COUNT(*) FROM issues WHERE parent_id IN ({})".format(issue))
    row = cur.fetchone()
    return row[0]>0
 