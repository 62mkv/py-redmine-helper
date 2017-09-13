import json
import requests
import re
from datetime import datetime
from utils import FixedOffset

auth_endpoint='/rest/auth/1'
# api_endpoint='/rest/api/2.0.alpha1' # - такой для JIRA 4.4
api_endpoint='/rest/api/2'

headers = {'user-agent': 'Python REST Client', 'content-type': 'application/json'}
MAX_RESULTS = 10 # сколько issues вернет JQL-запрос за один раз

real_query = True # костыль чтобы тестировать парсинг респонса на локальных данных

def parse_datetime(s):
    # 2017-08-15T05:08:00.000+0200
    m = re.match(r"^(.+)([\+\-]\d+)$", s)
    naive_dt = datetime.strptime(m.group(1), '%Y-%m-%dT%H:%M:%S.%f')
    offset_str = m.group(2)
    offset = int(offset_str[-4:-2])*60 + int(offset_str[-2:])
    if offset_str[0] == "-":
        offset = -offset
    return naive_dt.replace(tzinfo=FixedOffset(offset))

class JIRARESTAPIWrapper(object):

    def __init__(self, settings):
        self.host = settings.host
        self.auth_params = settings.auth_params
        self.project_name = settings.project_name
        (self.since_date, self.till_date) = (None, None)
        self.session = None
        self.worklogs = None

    def set_range(self, since_date, till_date):
        if (self.since_date != since_date or self.till_date != till_date):
            # initializing new range of data
            self.since_date = since_date
            self.till_date = till_date
            self.worklogs = None

    def auth(self):
        payload = self.auth_params
        r = requests.post(self.host+auth_endpoint+'/session', headers=headers, data=json.dumps(payload))
        return r.json()['session']['value']
    
    def query_results(self, url, params):
        if self.session is None:
            self.session = self.auth()
        cookies = {'JSESSIONID': self.session}
        return requests.get(url, params=params, headers=headers, cookies=cookies).json()

    def get_issues(self, start_at, max_results):
        payload = {'jql': 'worklogDate >= {} AND worklogDate <= {}'.format(self.since_date, self.till_date), 'maxResults': max_results, 'fields': 'worklog,-description', 'expand': 'names', 'startAt': start_at}
        return self.query_results(self.host+api_endpoint+'/search', payload)

    def get_worklogs(self, issue_id):
        payload = {'maxResults': MAX_RESULTS}
        return self.query_results(self.host+api_endpoint+'/issue/{}/worklog'.format(issue_id), payload)

    def load_worklogs(self):

        start_at = 0
        is_EOF = False

        worklog_data = []

        while not is_EOF:
            if real_query:
                response_result = self.get_issues(start_at, MAX_RESULTS)
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
                    worklogs = self.get_worklogs(issue_id)['worklogs']
                else:
                    worklogs = r['worklog']['worklogs'] 

                for wl in worklogs:
                    worklog_data.append((
                        issue, 
                        wl['author']['name'], 
                        parse_datetime(wl['started']).date(), 
                        wl['timeSpentSeconds'], 
                        parse_datetime(wl['created']).date(), 
                        wl['comment']
                    ))

            start_at += len(issues)
            if start_at>=total:
                is_EOF = True
            
            if not real_query: is_EOF = True

        self.worklogs = worklog_data

    def time_entries(self, user_id, projects, date):
        if self.worklogs is None: self.load_worklogs()

        result = []

        for wl in self.worklogs:
            wldate = wl[2].strftime('%Y-%m-%d')
            if wl[1] == user_id and str(wldate) == str(date):
                result.append([
                    self.project_name,
                    wl[0],
                    wldate,
                    wl[3] / 60.0 / 60.0,
                    wl[5].splitlines()[0] if len(wl[5].splitlines())>0 else '',
                    wl[4].strftime('%Y-%m-%d')
                ])

        return result
        

#print json.dumps(get_worklogs(10120))
#print parse_datetime('2017-08-15T05:08:00.000+0200')
