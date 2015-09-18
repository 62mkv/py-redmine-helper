﻿import json
from restful_lib import Connection
import settings

class easyRedmineWrapper:

    def __init__(self, api_key):
        self.api_key = api_key
        self.conn = Connection(settings.redmine_url)
    
    def request_put(self, path, payload):
        return self.conn.request_put(path, args= [ ('key', self.api_key) ], body=json.dumps(payload), headers={'content-type':'application/json', 'accept':'application/json'})

    def put_issues_with_payload(self, issues, payload):
        for i in issues:
            resp = self.request_put("/issues/"+str(i)+".json", {'issue': payload})
            status = resp[u'headers']['status']
            print 'Issue ', i, ', http status code: ', status

    def add_issues_to_milestone(self, issues, version_id, milestone_name):
        self.put_issues_with_payload(issues, {'notes': 'Issue added to milestone: '+milestone_name, 'fixed_version_id': version_id})

    def add_issues_on_sprint(self, issues, sprint_id, sprint_name):
        self.put_issues_with_payload(issues, {'notes': 'Issue added to sprint "'+sprint_name+'" from REST API', 'easy_sprint_id': sprint_id})
                                         
    def set_issues_status(self, issues, status_id):
        self.put_issues_with_payload(issues,{'status_id': status_id})

    def set_issues_status_and_assigned(self, issues, status_id, assigned_id):
        self.put_issues_with_payload(issues,{'status_id': status_id, 'assigned_to_id': assigned_id})

    def add_issues_to_milestone_1(self, issues):
        self.add_issues_to_milestone(issues, 61, "Milestone 1")

    def set_parent_issue(self, issues, parent_id):
        self.put_issues_with_payload(issues,{'parent_issue_id': parent_id})
