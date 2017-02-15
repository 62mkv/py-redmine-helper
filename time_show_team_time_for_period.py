from time_entry import print_team_time_spent_on_period
from datetime import date
from rminstance.common import teams
import sys

try:
    arg_teams=sys.argv[1]
    teamdict = {team:teams[team] for team in (set(teams.keys()) & set(arg_teams.split(',')))}
except:
    teamdict = teams

today = date.today()
start_of_month = today.replace(day=1)
print_team_time_spent_on_period(teamdict, (start_of_month, today))