import sys
import os
from datetime import date, timedelta
from prodcal import ProdCal

def get_issues_from_command_line_as_list():
    if len(sys.argv)<2:
       print "Usage: ",sys.argv[0]," <issue_id>[,<issue_id>]"
       sys.exit(2)

    try:
       issues = map(int,sys.argv[1].split(','))
    except:
       print "ERROR: argument #1 has to be comma-separated list of issue ids"
       sys.exit(1)

    return issues

def get_issues_from_command_line():
    return set(get_issues_from_command_line_as_list())

def get_folders_in_path(path):
    folders = []
    names = os.listdir(path)
    for folder in names: 
       try:
          os.listdir("{}\\{}".format(path, folder))
          folders.append(folder)
       except:
          pass

    return folders

def join_with(items, separator):
    return separator.join(map(str,items))

def as_in(items):
    return join_with(items, ', ')

def get_last_working_day(before=1):
    calendar = ProdCal()
    _d = date.today()
    count = 0
    while count<before:
        _d -= timedelta(days=1)
        while not calendar.is_work_day(_d):
            _d -= timedelta(days=1)
        count+=1
    return _d
  
