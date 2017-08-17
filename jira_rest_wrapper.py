import json
import requests 
import re
from datetime import datetime
from rminstance.fantasy.settings import host, auth_params
from utils import FixedOffset

auth_endpoint='/rest/auth/1'
api_endpoint='/rest/api/2'
headers = {'user-agent': 'Python REST Client', 'content-type': 'application/json'}
MAX_RESULTS = 10 # сколько issues вернет JQL-запрос за один раз
since_date = '2017-08-16' # с какой даты запрашиваем данные
session = None

def parse_datetime(s):
    # 2017-08-15T05:08:00.000+0200
    m = re.match("^(.+)([\+\-]\d+)$", s)
    naive_dt = datetime.strptime(m.group(1), '%Y-%m-%dT%H:%M:%S.%f')
    offset_str = m.group(2)
    offset = int(offset_str[-4:-2])*60 + int(offset_str[-2:])
    if offset_str[0] == "-":
        offset = -offset
    return naive_dt.replace(tzinfo=FixedOffset(offset))

def auth():
    payload = auth_params
    r = requests.post(host+auth_endpoint+'/session', headers=headers, data=json.dumps(payload))
    return r.json()['session']['value']

def query_results(url, params):
    global session
    if session is None:
        session = auth()
        #print session
    cookies = {'JSESSIONID': session}
    return requests.get(url, params=params, headers=headers, cookies=cookies).json()

def get_issues(start_at, max_results):
    payload = {'jql': 'worklogDate >= {}'.format(since_date), 'maxResults': max_results, 'fields': 'worklog,-description', 'expand': 'names', 'startAt': start_at}
    return query_results(host+api_endpoint+'/search', payload)

def get_worklogs(issue_id):
    payload = {'maxResults': MAX_RESULTS}
    return query_results(host+api_endpoint+'/issue/{}/worklog'.format(issue_id), payload)

def main(real_query):

    start_at = 0
    is_EOF = False

    worklog_data = []

    while not is_EOF:
        if real_query:
            response_result = get_issues(start_at, MAX_RESULTS)
        else:
            fp = open("jira-issues3.json")
            response_result = json.load(fp)

        #print json.dumps(response_result)

        start_at, total = (response_result['startAt'], response_result['total'])
        issues = response_result['issues']
        issue_worklogs = [{ 'issue': { 'key': x['key'], 'id': x['id'] }, 'worklog': x['fields']['worklog']} for x in issues]

        for r in issue_worklogs:
            issue = r['issue']['key']
            issue_id = r['issue']['id']
            wl_total = r['worklog']['total']
            wl_count = r['worklog']['maxResults']

            if wl_count<wl_total:
#                print "Issue {}:{} has {} worklogs and we have only {}".format(issue_id, issue, wl_total, wl_count)
                worklogs = get_worklogs(issue_id)['worklogs']
            else:
                worklogs = r['worklog']['worklogs'] 

            for wl in worklogs:
                worklog_data.append((issue, wl['author']['name'], parse_datetime(wl['started']).date(), wl['timeSpentSeconds']))

        start_at += len(issues)
        if start_at>=total:
            is_EOF = True
        
        if not real_query: is_EOF = True

    for issue, author, started, time_spent in worklog_data:
        print issue, author, started, time_spent

    return

main(True)
#print json.dumps(get_worklogs(10120))
#print parse_datetime('2017-08-15T05:08:00.000+0200')
