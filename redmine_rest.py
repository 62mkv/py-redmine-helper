from rminstance.easyredmine import settings as easysettings
from rminstance.freematiq   import settings as freesettings
from redmine_rest_wrapper import RedmineRESTAPIWrapper
# erw
erw = RedmineRESTAPIWrapper(easysettings)
frw = RedmineRESTAPIWrapper(freesettings)
