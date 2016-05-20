import json
from restful_lib import Connection
import re

class RedmineRESTAPIWrapper(object):

    def __init__(self, settings):
        self.api_key = settings.redmine_api_key
        self.conn = Connection(settings.redmine_url)
    
    def request_put(self, path, payload):
        return self.conn.request_put(path, args= [ ('key', self.api_key) ], body=json.dumps(payload), headers={'content-type':'application/json', 'accept':'application/json'})

    def request_post(self, path, payload):
        return self.conn.request_post(path, args= [ ('key', self.api_key) ], body=json.dumps(payload), headers={'content-type':'application/json', 'accept':'application/json'})

    def request_get(self, path, payload):
        return self.conn.request_get(path, args= [ ('key', self.api_key) ] + payload, headers={'content-type':'application/json', 'accept':'application/json'})

    def put_items_with_payload(self, url, payload_name, items, payload):
        if not isinstance(items, set):
            items = set([items])
        for i in items:
            resp = self.request_put("/{}/".format(url)+str(i)+".json", { payload_name: payload})
            status = resp[u'headers']['status']
            print 'Item {} '.format(url), i, ', http status code: ', status
            if int(status) != 200:
                print resp

    def put_issues_with_payload(self, issues, payload):
        return self.put_items_with_payload("issues", "issue", issues, payload)

    def put_versions_with_payload(self, versions, payload):
        return self.put_items_with_payload("versions", "version", versions, payload)

    def post_time_entries_with_payload(self, payload):
        resp = self.request_post("/time_entries.json", {'time_entry': payload})
        status = resp[u'headers']['status']
        print 'Issue ', payload['issue_id'], ', http status code: ', status

    def get_items_as_json(self, endpoint, payload):
	resp = self.request_get("/"+endpoint+".json", payload)
        status = resp[u'headers']['status']
        return resp[u'body']

    def get_time_entries(self, payload):
        return self.get_items_as_json('time_entries', payload)

    def get_projects(self, payload):
        return self.get_items_as_json('projects', payload)

    def set_projects_parent(self, projects, parent_id):
        return self.put_items_with_payload("projects", "project", projects, { 'parent_id': parent_id})

    def add_issues_to_milestone(self, issues, version_id, milestone_name):
        self.put_issues_with_payload(issues, {'notes': 'Issue added to milestone: '+milestone_name, 'fixed_version_id': version_id})

    def add_issues_on_sprint(self, issues, sprint_id, sprint_name):
        self.put_issues_with_payload(issues, {'notes': 'Issue added to sprint "'+sprint_name+'" from REST API', 'easy_sprint_id': sprint_id})
                                         
    def set_issues_status(self, issues, status_id):
        self.put_issues_with_payload(issues, {'status_id': status_id})

    def set_issues_status_and_assigned(self, issues, status_id, assigned_id):
        self.put_issues_with_payload(issues, {'status_id': status_id, 'assigned_to_id': assigned_id})

    def set_issues_assigned(self, issues, assigned_id):
        self.put_issues_with_payload(issues, {'assigned_to_id': assigned_id})

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

    def close_issues(self, issues):
        self.set_issues_status(issues, settings.statuses['closed'])

    def get_items_as_json_full(self, endpoint, params = None, process_cb = None):
        (offset, limit, read, total) = (0, 25, 0, 65535)
        if params is None: params = []
        result = []
        while read<total:
            _params = params + [('limit', limit), ('offset', offset)]
            resp = json.loads(self.get_items_as_json(endpoint, _params))
#            add_to_list(resp["time_entries"], label)
            result += resp[endpoint]
            if process_cb is not None:
                process_cb(resp[endpoint])

            total = resp["total_count"]
            read += limit if (limit+offset < total) else total - offset
            offset += limit
        return result
