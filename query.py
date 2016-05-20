
select_issues_in_backlog_for_sprint = """
    SELECT iesr.issue_id FROM issue_easy_sprint_relations iesr 
    JOIN issues i ON iesr.issue_id = i.id
     WHERE iesr.relation_type=1 and iesr.easy_sprint_id={sprint_id}
    """

select_issues_without_parents_on_milestone_X_not_on_project_Y = """
    SELECT id FROM issues WHERE parent_id IS NULL AND fixed_version_id={fixed_version_id} AND project_id!={project_id}
    """

select_open_issues_on_current_milestone_not_on_any_sprint = """
    SELECT i.id FROM issues i WHERE i.fixed_version_id={milestone_id} AND i.status_id NOT IN ({closed_statuses}) AND
    NOT EXISTS 
    (SELECT iesr.issue_id FROM issue_easy_sprint_relations iesr WHERE iesr.easy_sprint_id IS NOT NULL AND iesr.issue_id=i.id)
    """

select_root_issues_on_milestone = """
    SELECT id from issues WHERE fixed_version_id = {milestone_id} and parent_id is NULL
    """