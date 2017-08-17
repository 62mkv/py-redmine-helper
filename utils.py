import sys
import argparse
import os
from datetime import date, datetime, timedelta, tzinfo
from prodcal import ProdCal

class FixedOffset(tzinfo):
    """Fixed offset in minutes: `time = utc_time + utc_offset`."""
    def __init__(self, offset):
        self.__offset = timedelta(minutes=offset)
        hours, minutes = divmod(offset, 60)
        #NOTE: the last part is to remind about deprecated POSIX GMT+h timezones
        #  that have the opposite sign in the name;
        #  the corresponding numeric value is not used e.g., no minutes
        self.__name = '<%+03d%02d>%+d' % (hours, minutes, -hours)
    def utcoffset(self, dt=None):
        return self.__offset
    def tzname(self, dt=None):
        return self.__name
    def dst(self, dt=None):
        return timedelta(0)
    def __repr__(self):
        return 'FixedOffset(%d)' % (self.utcoffset().total_seconds() / 60)

def valid_date(string):
    try:
        dt = datetime.strptime(string,"%d-%m-%Y")
    except:
        msg = "%r is not a valid date" % string
        raise argparse.ArgumentTypeError(msg)
    return date(dt.year,dt.month,dt.day)

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

def get_last_day_before(before, only_work_days):
    calendar = ProdCal()
    _d = date.today()
    count = 0
    while count<before:
        _d -= timedelta(days=1)
        if only_work_days:
            while not calendar.is_work_day(_d):
                _d -= timedelta(days=1)
        count+=1
    return _d
  
def date_range(start, end):
    start =datetime.strptime(start, "%Y-%m-%d")
    end =datetime.strptime(end, "%Y-%m-%d")
    return [start + timedelta(days=x) for x in range(0, (end-start).days + 1)]