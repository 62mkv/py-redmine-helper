import subprocess
import settings
import re

def list_branch_issues(repo,branch):
    issues = []
    try:
        diff = subprocess.check_output("git --git-dir={0} log --oneline master..origin/{1}".format(settings.repo_storage+'\\'+repo+'\\\.git',branch),stderr = subprocess.STDOUT)
    except subprocess.CalledProcessError, e:
        if not e.returncode == 128:
            print "Error in repo '{0}' when build diff of origin/{1} with master: {2}".format(repo,branch,e.output)
        else: 
            print "ERROR: Repo {}, unknown branch in origin: {}".format(repo,branch)
        return issues
    for line in diff.split():
        mp = re.match('#(\d+)',line)
        if mp is not None:
            issue = int(mp.group(1))
            issues += [issue]
    return set(issues)

def get_remote_branches_for_commit(repo,commit):
    remote_branches = []
    contains = subprocess.check_output("git --git-dir={0} branch -a --contains {1}".format(settings.repo_storage+'\\'+repo+'\\\.git',commit))
          
    for line in contains.split():
        mp = re.match('\s*remotes/origin/(\S+)',line)
        if mp is not None:
            remote_branch = mp.group(1)
            remote_branches += [remote_branch]
    return remote_branches

