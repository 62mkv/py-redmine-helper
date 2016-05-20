from redmine_rest import erw, frw
from rminstance.easyredmine import settings as easysettings
from rminstance.freematiq   import settings as freesettings
from rminstance.easyredmine import team as easyteam
from rminstance.freematiq   import team as freeteam

from collections import namedtuple

RMInstance = namedtuple('RMInstance','rest_wrapper,label,settings,team');

rminstances = [
      RMInstance._make([erw, "ER", easysettings, easyteam]),
      RMInstance._make([frw, "FM", freesettings, freeteam])
   ]
