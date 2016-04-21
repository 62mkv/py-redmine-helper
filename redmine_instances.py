from redmine_rest import erw, frw
from rminstance.easyredmine import settings as easysettings
from rminstance.freematiq   import settings as freesettings
from collections import namedtuple

RMInstance = namedtuple('RMInstance','rest_wrapper,label,settings');

rminstances = [
      RMInstance._make([erw, "ER", easysettings]),
      RMInstance._make([frw, "FR", freesettings])
   ]
