# import the standard JSON parser
import json
import settings
# import the REST library
from restful_lib import Connection

class easyRedmineWrapper:

    def __init__(self):
        self.conn = Connection(settings.redmine_url)
    
    def request_put(self, path, payload):
        return self.conn.request_put(path, args= [ ('key', settings.redmine_api_key) ], body=json.dumps(payload), headers={'content-type':'application/json', 'accept':'application/json'})
