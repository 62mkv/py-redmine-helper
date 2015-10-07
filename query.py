
select_issues_in_backlog_for_sprint="""SELECT iesr.issue_id FROM issue_easy_sprint_relations iesr 
  JOIN issues i ON iesr.issue_id = i.id
  WHERE iesr.relation_type=1 and iesr.easy_sprint_id={sprint_id}"""

select_issues_without_parents_on_milestone_X_not_on_project_Y="SELECT id FROM issues WHERE parent_id IS NULL AND fixed_version_id={fixed_version_id} AND project_id!={project_id}"