from easyRedmine import easyRedmineWrapper

def put_issues_with_payload(issues, payload):
    erw = easyRedmineWrapper()

    for i in issues:
        resp = erw.request_put("/issues/"+str(i)+".json", {'issue': payload})
        status = resp[u'headers']['status']
        print 'Issue ', i, ', http status code: ', status

def add_issues_to_milestone(issues, version_id, milestone_name):
    put_issues_with_payload(issues, {'notes': 'Issue added to milestone: '+milestone_name, 'fixed_version_id': version_id})

def add_issues_on_sprint(issues, sprint_id, sprint_name):
    put_issues_with_payload(issues, {'notes': 'Issue added to sprint "'+sprint_name+'" from REST API', 'easy_sprint_id': sprint_id})
                                     
def set_issues_status(issues, status_id):
    put_issues_with_payload(issues,{'status_id': status_id})

def set_issues_status_and_assigned(issues, status_id, assigned_id):
    put_issues_with_payload(issues,{'status_id': status_id, 'assigned_to_id': assigned_id})

def add_issues_to_milestone_1(issues):
    add_issues_to_milestone(issues, 61, "Milestone 1")

def set_parent_issue(issues, parent_id):
    put_issues_with_payload(issues,{'parent_issue_id': parent_id})