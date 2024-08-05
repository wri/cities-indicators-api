from app.const import projects_table

def list_projects():
    projects = projects_table.all(view="api", formula="{project_id}")
    projects_dict = {project['fields']['project_id'] for project in projects}
    
    return projects_dict
