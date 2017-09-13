from time_entry import print_team_time_spent_on_period
from datetime import date, datetime, timedelta
from rminstance.common import teams, active_teams
from utils import valid_date

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--team", help='one or several (comma-separated) of keys of "teams" dict, declared in rminstance/common.py. When a valid team is specified, only data for this team is collected.')
parser.add_argument("--from", dest='fromdate', help='specify start date of period in dd-mm-yyyy format', type=valid_date)
parser.add_argument("--to", dest='todate', help='specify end date of period in dd-mm-yyyy format', type=valid_date)
args=parser.parse_args()

try:
    arg_teams=args.team
    teamdict = {team:teams[team] for team in (set(teams.keys()) & set(arg_teams.split(',')))}
except:
    if active_teams is not None:
        print "Summarize only active teams from rminstance/common.py:", active_teams
        teamdict = { k: v for k, v in teams.items() if k in active_teams }
    else:
        teamdict = teams

today = date.today()

# on the first day of month, collect data for previous month
if today.day == 1: 
    end_of_period = args.todate if args.todate else today
    today -= timedelta(days=1)
    start_of_period = args.fromdate if args.fromdate else today.replace(day=1)
else:
    start_of_period = args.fromdate if args.fromdate else today.replace(day=1)
    end_of_period = args.todate if args.todate else today

print_team_time_spent_on_period(teamdict, (start_of_period, end_of_period))
