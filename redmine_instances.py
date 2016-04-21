from redmine_rest import erw, frw
from rminstance.easyredmine import settings as easysettings
from rminstance.freematiq   import settings as freesettings

rminstances = [
      (erw, "ER", easysettings),
      (frw, "FR", freesettings)
   ]
