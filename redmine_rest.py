import json
from restful_lib import Connection
import re
import settings

class easyRedmineWrapper:

    def __init__(self, api_key = settings.redmine_api_key):
        self.api_key = api_key
        self.conn = Connection(settings.redmine_url)
    
    def request_put(self, path, payload):
        return self.conn.request_put(path, args= [ ('key', self.api_key) ], body=json.dumps(payload), headers={'content-type':'application/json', 'accept':'application/json'})

    def put_issues_with_payload(self, issues, payload):
        if not isinstance(issues, set):
            issues = set([issues])
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

    def set_parent_issue(self, issues, parent_id):
        self.put_issues_with_payload(issues,{'parent_issue_id': parent_id})

    def add_notes_on_issues(self, issues, notes):
        self.put_issues_with_payload(issues,{'notes': notes})

    def add_update_on_commit(self, issue, repo_name, branch_name, commit_hash, commit_msg):
        notes = "Repo <b>%s</b> branch <b>%s</b> commit <b>%s</b>: %s" % (repo_name, branch_name, commit_hash, commit_msg)
        return self.add_notes_on_issues(set([issue]), notes)

    def add_update_on_commit_from_line(self, line, repo_name, branch_name):
        (commit_hash, commit_msg) =line.split(' ',1)
        match = re.search("\#(\d+)", commit_msg)
        if match:
            issue = match.group(1)
            resp =self.add_update_on_commit(issue,repo_name, branch_name, commit_hash, commit_msg)

    def add_issues_to_milestone_1(self, issues):
        self.add_issues_to_milestone(issues, 61, "Milestone 1")

erw = easyRedmineWrapper()
