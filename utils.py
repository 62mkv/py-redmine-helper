import sys

def get_issues_from_command_line():
    if len(sys.argv)<2:
       print "Usage: ",sys.argv[0]," <issue_id>[,<issue_id>]"
       sys.exit(2)

    try:
       issues = map(int,sys.argv[1].split(','))
    except:
       print "ERROR: argument #1 has to be comma-separated list of issue ids"
       sys.exit(1)

    return set(issues)