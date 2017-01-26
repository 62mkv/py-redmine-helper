import utils
from rminstance import common
from redmine_instances import rminstances
from collections import namedtuple
from datetime import timedelta

TimeEntry = namedtuple('TimeEntry', 'rminstance,project,issue,spent_on,hours,comment,created_on')


def print_user_time_entries(time_entries, date):
    total = 0
    time_entries.sort(key=lambda x: x.created_on)
    for te in time_entries:
        if str(te.spent_on) == str(date):
            print utils.join_with(te, u'\t')
            total += te.hours

    print total


def get_user_time_entries(user, date):
    """
    This function gets time_entries for a given user on a given date from all configured RMs via REST API
    :param user: user-name, for which we collect the data, like 'ivanov'
    :param date: date, for which we collect the data, like '2016-02-22'
    :type user: basestring
    :type date: datetime.date
    :return: list of named tuples of type 'TimeEntry'
    """
    time_entries = list()

    for rminstance in rminstances:
        if rminstance.team.team.get(user) is not None:
            projects = rminstance.settings.projects_with_time
            rw = rminstance.rest_wrapper
            label = rminstance.label
            user_id = rminstance.team.team[user]
            for project in projects:
                params = [('project_id', project), ('user_id', user_id), ('spent_on', date)]
                for te in rw.get_items_as_json_full('time_entries', params):
                    time_entries.append(TimeEntry._make(
                        [label, te['project']['name'], te['issue']['id'] if te.get('issue') is not None else None, te['spent_on'],
                         te['hours'], te['comments'], te['created_on']]))

        else:
            print "User {} not found in instance {}".format(user, rminstance.label)

    return time_entries


def get_team_time_entries(team, date):
    """
    Get a dict of time entries for each user of a team on a given date
    :param team: list of user names, ex: ['ivanov','obama']
    :param date: date
    :return: dict { 'username': [list, of, TimeEntry, named, tuples] }
    """
    users = set()
    for user in team:
        users |= {user}

    user_time_entries = dict()
    for user in users:
        user_time_entries[user] = get_user_time_entries(user, date)

    return user_time_entries


def load_time_entries(rw, params, function):
    return rw.get_items_as_json_full('time_entries', params, function)


def show_teams_time_entries(teams, date):
    """
    Display time entries for a dict of teams
    :param teams: dict of { 'teamname1': ['user1','user2,'...'] }
    :param date:
    :return: None
    """
    for team in teams:
        user_time_entries = get_team_time_entries(teams[team], date)
        for u, te in user_time_entries.iteritems():
            print u
            print_user_time_entries(te, date)


def print_team_time_spent_on_period(_users, period):
    """
    Displays summary type spent in a given period by members of each of the teams
    :param teams: teams: dict of { 'teamname1': ['user1','user2,'...'] }
    :param period: tuple of (date1, date2)
    :return: None
    """
    users = set()
    if isinstance(_users, dict):
        for team in _users:
            users |= set(_users[team])
    elif isinstance(_users, int):
        users = set([_users])
    elif isinstance(_users, list):
        users = set(_users)

    date = period[0]
    date_time_entries = dict()
    while date < period[1]:
        date_time_entries[date] = dict()
        for user in users:
            date_time_entries[date][user] = reduce(lambda x,y: x+y, get_user_time_entries(user, date), 0)
        date += timedelta(1)

    print date_time_entries


def print_team_time_spent_before(teams, before=0):
    return show_teams_time_entries(teams, utils.get_last_working_day(before))


def print_my_time_spent_before(before=0):
    date = utils.get_last_working_day(before)
    return  print_user_time_entries(get_user_time_entries(common.me, date), date)

