import os
import json
from datetime import datetime
from engine.ast_parser import parse_project_documents
from engine.traceability_builder import build_traceability_edges
from engine.audit_engine import check_audit_rules
from engine.git_analyzer import analyze_git_repo

DEFAULT_PROJECTS = {
    "projects": [
        {
            "id": "ProjectCult",
            "name": "Project Cult",
            "local_root": "C:/repo/3_UE5_ProjectCult/",
            "docs_path": "C:/repo/3_UE5_ProjectCult/docs/ProjectDocuments/",
            "rules_path": "C:/repo/3_UE5_ProjectCult/docs/Standarts/",
            "github_url": "",
            "last_scan": None,
            "created_at": "2026-05-31T17:45:00"
        }
    ]
}

def load_projects(projects_file):
    """
    Loads projects.json file. Creates default if not exists.
    """
    if not os.path.exists(projects_file):
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(projects_file) or ".", exist_ok=True)
        with open(projects_file, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_PROJECTS, f, indent=2, ensure_ascii=False)
        return DEFAULT_PROJECTS["projects"]
        
    try:
        with open(projects_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("projects", [])
    except Exception as e:
        print(f"Error loading projects: {e}")
        return DEFAULT_PROJECTS["projects"]

def save_projects(projects_file, projects):
    """
    Saves projects list to projects.json
    """
    payload = {"projects": projects}
    try:
        os.makedirs(os.path.dirname(projects_file) or ".", exist_ok=True)
        with open(projects_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving projects: {e}")
        return False

def add_project(projects_file, new_project):
    """
    Adds a new project configurations.
    """
    projects = load_projects(projects_file)
    
    # Check if project with same ID already exists
    for p in projects:
        if p["id"] == new_project["id"]:
            return False, "Project ID already exists."
            
    new_project["created_at"] = datetime.now().isoformat()
    new_project["last_scan"] = None
    
    projects.append(new_project)
    save_projects(projects_file, projects)
    return True, "Project added successfully."

def delete_project(projects_file, project_id):
    projects = load_projects(projects_file)
    filtered = [p for p in projects if p["id"] != project_id]
    
    if len(filtered) == len(projects):
        return False, "Project not found."
        
    save_projects(projects_file, filtered)
    return True, "Project deleted successfully."

def update_project(projects_file, project_id, updated_data):
    projects = load_projects(projects_file)
    found = False
    
    for p in projects:
        if p["id"] == project_id:
            p.update(updated_data)
            found = True
            break
            
    if not found:
        return False, "Project not found."
        
    save_projects(projects_file, projects)
    return True, "Project updated successfully."

def scan_project(project_id, project_config, offline_data_dir):
    """
    Runs a full requirement scan + audit + git analysis for a project.
    Saves the results as offline JSON data for dual online/offline compatibility.
    """
    docs_path = project_config.get("docs_path")
    local_root = project_config.get("local_root")
    
    # Paths for manual entries inside docs folder
    manual_req_path = os.path.join(docs_path, "manual_requirements.json") if docs_path else None
    manual_edges_path = os.path.join(docs_path, "manual_edges.json") if docs_path else None
    
    # Load manual edges if present
    manual_edges = []
    if manual_edges_path and os.path.exists(manual_edges_path):
        try:
            with open(manual_edges_path, "r", encoding="utf-8") as f:
                manual_edges = json.load(f)
        except Exception as e:
            print(f"Error loading manual edges: {e}")

    # 1. Parse markdown documents + merge manual entries
    nodes = parse_project_documents(docs_path, manual_req_path)
    
    # 2. Establish traceability connections + manual links
    edges = build_traceability_edges(docs_path, nodes, manual_edges)
    
    # 3. Perform static audit validation
    audit_results = check_audit_rules(nodes, edges)
    
    # 4. Extract Git logs
    git_results = analyze_git_repo(local_root)
    
    # Bundle everything into a complete snapshot
    scan_payload = {
        "project_id": project_id,
        "name": project_config.get("name", project_id),
        "last_scan": datetime.now().isoformat(),
        "nodes": nodes,
        "edges": edges,
        "audit": audit_results,
        "git": git_results
    }
    
    # Save for offline usage in _LM_ALM_System/alm_offline_data/{project_id}.json
    os.makedirs(offline_data_dir, exist_ok=True)
    offline_file = os.path.join(offline_data_dir, f"{project_id}.json")
    try:
        with open(offline_file, "w", encoding="utf-8") as f:
            json.dump(scan_payload, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving offline JSON snapshot: {e}")
        
    return scan_payload
