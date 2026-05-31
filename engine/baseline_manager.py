import os
import json
from datetime import datetime

def create_baseline(project_id, label, data, baselines_root):
    """
    Saves a snapshot of the project state to baselines/{project_id}/{timestamp}.json
    """
    project_baselines_dir = os.path.join(baselines_root, project_id)
    os.makedirs(project_baselines_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}.json"
    filepath = os.path.join(project_baselines_dir, filename)
    
    baseline_payload = {
        "project_id": project_id,
        "label": label or f"Baseline_{timestamp}",
        "timestamp": datetime.now().isoformat(),
        "nodes": data.get("nodes", {}),
        "edges": data.get("edges", []),
        "stats": data.get("audit", {}).get("stats", {})
    }
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(baseline_payload, f, indent=2, ensure_ascii=False)
        
    return {
        "timestamp": timestamp,
        "label": baseline_payload["label"],
        "filename": filename
    }

def list_baselines(project_id, baselines_root):
    """
    Lists all baselines saved for a given project_id.
    """
    project_baselines_dir = os.path.join(baselines_root, project_id)
    if not os.path.exists(project_baselines_dir):
        return []
        
    baselines = []
    for file in os.listdir(project_baselines_dir):
        if file.endswith(".json"):
            filepath = os.path.join(project_baselines_dir, file)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                    baselines.append({
                        "timestamp": file.replace(".json", ""),
                        "label": meta.get("label", file),
                        "date": meta.get("timestamp", "")
                    })
            except Exception as e:
                print(f"Error reading baseline {file}: {e}")
                
    # Sort baselines by date descending
    baselines.sort(key=lambda x: x["timestamp"], reverse=True)
    return baselines

def compare_baselines(baseline_a, baseline_b):
    """
    Compares two baseline payloads and returns the difference in nodes and edges.
    """
    nodes_a = baseline_a.get("nodes", {})
    nodes_b = baseline_b.get("nodes", {})
    
    edges_a = baseline_a.get("edges", [])
    edges_b = baseline_b.get("edges", [])
    
    added_nodes = []
    deleted_nodes = []
    modified_nodes = []
    
    # Compare nodes
    for nid, node_b in nodes_b.items():
        if nid not in nodes_a:
            added_nodes.append({
                "id": nid,
                "title": node_b.get("title", ""),
                "level": node_b.get("level", "")
            })
        else:
            node_a = nodes_a[nid]
            # Check for changes in title or description
            changes = {}
            if node_a.get("title") != node_b.get("title"):
                changes["title"] = {"old": node_a.get("title"), "new": node_b.get("title")}
            if node_a.get("desc") != node_b.get("desc"):
                changes["desc"] = {"old": node_a.get("desc")[:50] + "...", "new": node_b.get("desc")[:50] + "..."}
                
            if changes:
                modified_nodes.append({
                    "id": nid,
                    "title": node_b.get("title", ""),
                    "level": node_b.get("level", ""),
                    "changes": changes
                })
                
    for nid, node_a in nodes_a.items():
        if nid not in nodes_b:
            deleted_nodes.append({
                "id": nid,
                "title": node_a.get("title", ""),
                "level": node_a.get("level", "")
            })
            
    # Compare edges (represent edges as a set of tuple strings for comparison)
    def edge_key(e):
        return f"{e['source']}->{e['target']}"
        
    keys_a = {edge_key(e): e for e in edges_a}
    keys_b = {edge_key(e): e for e in edges_b}
    
    added_edges = []
    deleted_edges = []
    
    for key, edge in keys_b.items():
        if key not in keys_a:
            added_edges.append(edge)
            
    for key, edge in keys_a.items():
        if key not in keys_b:
            deleted_edges.append(edge)
            
    return {
        "added_nodes": added_nodes,
        "deleted_nodes": deleted_nodes,
        "modified_nodes": modified_nodes,
        "added_edges": added_edges,
        "deleted_edges": deleted_edges
    }
