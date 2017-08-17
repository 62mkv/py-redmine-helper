from redmine_rest import erw, frw
from jira_rest import fantasy
from rminstance.easyredmine import settings as easysettings
from rminstance.freematiq   import settings as freesettings
from rminstance.fantasy     import settings as fantasysettings
from rminstance.easyredmine import team as easyteam
from rminstance.freematiq   import team as freeteam
from rminstance.fantasy     import team as fantasyteam

from collections import namedtuple

RMInstance = namedtuple('RMInstance','rest_wrapper,label,settings,team')

rminstances = [RMInstance._make(t) for t in
               [
                   [erw, "ER", easysettings, easyteam],
                   [frw, "FM", freesettings, freeteam],
                   [fantasy, "DFS", fantasysettings, fantasyteam],
               ]
              ]
