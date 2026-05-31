from engine.audit_engine import build_adjacency

def get_downstream_impact(node_id, nodes, edges):
    """
    Recursively calculates the downstream nodes affected by a change in node_id.
    Follows forward edges (upstream -> downstream).
    """
    if node_id not in nodes:
        return {
            "impacted_nodes": [],
            "ripple_score": 0.0,
            "risk_level": "LOW"
        }

    adj_forward, _ = build_adjacency(nodes, edges)
    
    impacted = {} # node_id -> depth
    queue = [(node_id, 0)]
    
    while queue:
        current, depth = queue.pop(0)
        
        # Traverse downstream children
        for child in adj_forward.get(current, []):
            if child not in impacted:
                impacted[child] = depth + 1
                queue.append((child, depth + 1))
                
    # Calculate Ripple Effect Score
    total_nodes = len(nodes)
    impacted_count = len(impacted)
    
    ripple_score = 0.0
    if total_nodes > 0:
        ripple_score = round((impacted_count / total_nodes) * 100, 1)
        
    # Determine risk level
    if ripple_score > 30.0:
        risk_level = "CRITICAL"
    elif ripple_score > 15.0:
        risk_level = "HIGH"
    elif ripple_score > 5.0:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"
        
    # Format list of impacted nodes with titles and levels
    impacted_list = []
    for mid, depth in impacted.items():
        ninfo = nodes.get(mid, {})
        impacted_list.append({
            "id": mid,
            "title": ninfo.get("title", "Unknown"),
            "level": ninfo.get("level", "Unknown"),
            "file": ninfo.get("file", ""),
            "depth": depth
        })
        
    return {
        "impacted_nodes": impacted_list,
        "ripple_score": ripple_score,
        "risk_level": risk_level
    }
