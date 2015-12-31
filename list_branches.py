from redmine_git import list_non_deployed_issues_from_branch, list_remote_branches
from redmine_mysql import get_statuses, get_issues_with_statuses
from utils import get_folders_in_path
import settings

repos = get_folders_in_path(settings.repo_storage)

for repo in repos:
    print repo
    branches = list(set(list_remote_branches(repo)) - {'master'})
    branches.sort()

    for branch in branches:
        issues = list_non_deployed_issues_from_branch(repo, 'origin/'+branch)
        issues_in_status = get_issues_with_statuses(issues)
        status_dict = get_statuses()
        print "\t{}".format(branch)
        for status in issues_in_status.keys():
            print "\t\t{}: {}".format(status_dict[status], issues_in_status[status])
