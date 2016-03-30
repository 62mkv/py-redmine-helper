import subprocess
import settings
import re

def get_git_dir(repo):
    return settings.repo_storage+'\\'+repo+'\\.git'

def list_branch_issues(repo,branch):
    issues = []
    try:
        diff = subprocess.check_output("git --git-dir={0} log --oneline origin/master..origin/{1}".format(get_git_dir(repo),branch),
            stderr = subprocess.STDOUT)
    except subprocess.CalledProcessError, e:
        if e.returncode == 128:
            print "ERROR: Repo {}, unknown branch in origin: {}".format(repo,branch)
        else: 
            print "Error in repo '{0}' when build diff of origin/{1} with origin/master: {2}".format(repo,branch,e.output)
        return issues
    for line in diff.split():
        mp = re.match('#(\d+)',line)
        if mp is not None:
            issue = int(mp.group(1))
            issues += [issue]
    return set(issues)

def list_remote_branches(repo, options=None, commit=None):
    remote_branches = []
    try:
        command = "git --git-dir={0} branch -r {1}".format(
           get_git_dir(repo),
           str(options) if options is not None else "")
        contains = subprocess.check_output(command)
    except subprocess.CalledProcessError, e:
        if e.returncode == 129: 
            print "Unappropriate commit {} in repo {}".format(commit, repo)
        else:
            print "Error in repo '{}' when listing branches for commit {}: {}".format(repo, commit, e.output)
        return remote_branches

    for line in contains.split():
        mp = re.match('\s*(?:remotes/)?origin/(\S+)',line)
        if mp is not None:
            remote_branch = mp.group(1)
            if remote_branch != 'HEAD': remote_branches += [remote_branch] 
    return remote_branches

def get_remote_branches_for_commit(repo, commit):
    return list_remote_branches(repo,  "-r --contains {}".format(commit),commit)

def list_non_deployed_issues_from_branch(repo, branch):
    issues = set()
    command = "git --git-dir={0} log --oneline master..{1}".format(get_git_dir(repo), branch)
    try:
        contains = subprocess.check_output(command)
    except subprocess.CalledProcessError, e:
        print e.output
        return issues

    for line in contains.split():
        mp = re.search('#([0-9]+)', line)
        if mp is not None:
           issue = int(mp.group(1))
           issues.add(issue)

    return issues
