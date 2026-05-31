import re

def get_level_category(tag):
    if tag.startswith("REQ_VD_"): return "L0"
    if tag.startswith("REQ_GDD_"): return "L1"
    if tag.startswith("REQ_NDD_"): return "L2"
    if tag.startswith("REQ_TDD_"): return "L3-C"
    if tag.startswith("REQ_ADD_"): return "L3-D"
    if tag.startswith("PBI"): return "L4"
    if tag.startswith("TC_QA_"): return "L5"
    return "UNKNOWN"

def build_adjacency(nodes, edges):
    """
    Builds forward and backward adjacency maps.
    """
    adj_forward = {node_id: [] for node_id in nodes}
    adj_backward = {node_id: [] for node_id in nodes}
    
    # Initialize entries for any target or source not explicitly in nodes
    for edge in edges:
        src = edge["source"]
        tgt = edge["target"]
        if src not in adj_forward:
            adj_forward[src] = []
            adj_backward[src] = []
        if tgt not in adj_forward:
            adj_forward[tgt] = []
            adj_backward[tgt] = []
            
        adj_forward[src].append(tgt)
        adj_backward[tgt].append(src)
        
    return adj_forward, adj_backward

def has_path_to_level(node_id, target_level, adj_backward, nodes, visited=None):
    """
    Checks if a node has an upward path to a node of the target_level (e.g. L0).
    Uses BFS/DFS along reverse edges.
    """
    if visited is None:
        visited = set()
        
    if node_id in visited:
        return False
    visited.add(node_id)
    
    # Check if this node itself is of the target level
    node_info = nodes.get(node_id)
    if node_info:
        level = node_info.get("level", "")
        if target_level in level:
            return True
            
    # Traverse backwards to parents
    for parent in adj_backward.get(node_id, []):
        if has_path_to_level(parent, target_level, adj_backward, nodes, visited):
            return True
            
    return False

def has_path_to_node(node_id, target_node_id, adj_backward, visited=None):
    """
    Checks if there is a path from node_id to target_node_id along backward/parent edges.
    """
    if visited is None:
        visited = set()
        
    if node_id in visited:
        return False
    visited.add(node_id)
    
    if node_id == target_node_id:
        return True
        
    for parent in adj_backward.get(node_id, []):
        if has_path_to_node(parent, target_node_id, adj_backward, visited):
            return True
            
    return False

def parse_story_points(node):
    text = (node.get("title", "") + " " + node.get("desc", "")).lower()
    # Match patterns like: SP: 5, Story Point: 8, SP = 13, 5 SP, 8 Puan
    sp_match = re.search(r"(?:sp|story\s*point|efor|point|puan|sp)\s*[:= ]\s*([0-9]+)", text)
    if sp_match:
        return int(sp_match.group(1))
    # Look for standalone number followed by sp or story point
    sp_match_rev = re.search(r"\b([0-9]+)\s*(?:sp|story\s*point|puan|efor)\b", text)
    if sp_match_rev:
        return int(sp_match_rev.group(1))
    return None

def check_audit_rules(nodes, edges):
    """
    Performs static analysis based on 12 ASPICE Level 3 audit rules.
    Returns {alerts: [...], stats: {...}, health_score: float, coverage_matrix: {...}}
    """
    alerts = []
    adj_forward, adj_backward = build_adjacency(nodes, edges)
    
    # Rule stats counters
    rule_violations = {f"Rule_{i}": 0 for i in range(1, 13)}
    
    # Parse test statuses from files/nodes (mock default to Untested, we can enhance later)
    # E.g. TC_QA nodes can have status PASS, FAIL, UNTESTED
    test_statuses = {}
    for node_id, node in nodes.items():
        if node_id.startswith("TC_QA_"):
            # Simple text status parser from description
            desc = node.get("desc", "").upper()
            title = node.get("title", "").upper()
            combined = desc + " " + title
            
            if "PASSED" in combined or "[X] PASSED" in combined or "PASS" in combined:
                test_statuses[node_id] = "PASS"
            elif "FAILED" in combined or "[X] FAILED" in combined or "FAIL" in combined:
                test_statuses[node_id] = "FAIL"
            else:
                test_statuses[node_id] = "UNTESTED"

    # Evaluate nodes
    for node_id, node in nodes.items():
        level = node.get("level", "")
        level_cat = get_level_category(node_id)
        
        # Rule 1: Orphan Rule (L1-L3 requirements must trace back to L0)
        if level_cat in ["L1", "L2", "L3-C", "L3-D"]:
            if not has_path_to_level(node_id, "L0", adj_backward, nodes):
                alerts.append({
                    "node_id": node_id,
                    "rule": "Rule_1",
                    "type": "ORPHAN_ERROR",
                    "message": f"{node_id} ({level}) herhangi bir L0 (Vision) gereksinimine bağlanmıyor (Yetim Düğüm)."
                })
                rule_violations["Rule_1"] += 1
                
        # Rule 2: QA Coverage (Every L4 PBI must link to at least 1 QA Test Case)
        if level_cat == "L4":
            linked_qa = [tgt for tgt in adj_forward.get(node_id, []) if tgt.startswith("TC_QA_")]
            linked_qa_back = [src for src in adj_backward.get(node_id, []) if src.startswith("TC_QA_")]
            all_linked_qa = list(set(linked_qa + linked_qa_back))
            
            if not all_linked_qa:
                alerts.append({
                    "node_id": node_id,
                    "rule": "Rule_2",
                    "type": "QA_GAP",
                    "message": f"{node_id} (PBI) için herhangi bir QA Test Senaryosu (L5) tanımlanmamış."
                })
                rule_violations["Rule_2"] += 1
                
            # Rule 11: Fibonacci Story Points
            sp = parse_story_points(node)
            if sp is not None:
                fib_points = {1, 2, 3, 5, 8, 13, 21}
                if sp not in fib_points:
                    alerts.append({
                        "node_id": node_id,
                        "rule": "Rule_11",
                        "type": "FORMAT_ERROR",
                        "message": f"{node_id} Story Point değeri ({sp}) Fibonacci serisine uygun değil {fib_points}."
                    })
                    rule_violations["Rule_11"] += 1
            else:
                # SP Missing warning (not a failure but warning)
                pass

            # Rule 12: DoD Compliance
            desc_lower = node.get("desc", "").lower()
            if "dod" not in desc_lower and "definition of done" not in desc_lower and "kabul kriteri" not in desc_lower:
                alerts.append({
                    "node_id": node_id,
                    "rule": "Rule_12",
                    "type": "COMPLIANCE_GAP",
                    "message": f"{node_id} (PBI) için Definition of Done (DoD) veya Kabul Kriteri belirtilmemiş."
                })
                rule_violations["Rule_12"] += 1
                
        # Rule 3: Stability Rule (FAIL test blocks PBI stability)
        if level_cat == "L5":
            status = test_statuses.get(node_id, "UNTESTED")
            if status == "FAIL":
                # Find PBIs linked to this test case
                parents = adj_backward.get(node_id, []) + adj_forward.get(node_id, [])
                linked_pbis = [p for p in parents if p.startswith("PBI")]
                for pbi in linked_pbis:
                    alerts.append({
                        "node_id": pbi,
                        "rule": "Rule_3",
                        "type": "STABILITY_BLOCK",
                        "message": f"{pbi} (PBI), başarısız olan {node_id} test senaryosu nedeniyle kilitlendi / kararsız durumda."
                    })
                    rule_violations["Rule_3"] += 1

        # Rule 4: GDD -> VD Trace
        if level_cat == "L1":
            parents = adj_backward.get(node_id, [])
            vd_parents = [p for p in parents if p.startswith("REQ_VD_")]
            if not vd_parents:
                alerts.append({
                    "node_id": node_id,
                    "rule": "Rule_4",
                    "type": "TRACE_GAP",
                    "message": f"{node_id} (GDD) doğrudan bir REQ_VD_* (L0) gereksinimine bağlanmıyor."
                })
                rule_violations["Rule_4"] += 1

        # Rule 5: TDD -> GDD Trace
        if level_cat == "L3-C":
            parents = adj_backward.get(node_id, [])
            gdd_parents = [p for p in parents if p.startswith("REQ_GDD_")]
            if not gdd_parents:
                alerts.append({
                    "node_id": node_id,
                    "rule": "Rule_5",
                    "type": "TRACE_GAP",
                    "message": f"{node_id} (TDD) doğrudan bir REQ_GDD_* (L1) gereksinimine bağlanmıyor."
                })
                rule_violations["Rule_5"] += 1

        # Rule 6: ADD -> GDD/VD Trace
        if level_cat == "L3-D":
            parents = adj_backward.get(node_id, [])
            valid_parents = [p for p in parents if p.startswith("REQ_GDD_") or p.startswith("REQ_VD_")]
            if not valid_parents:
                alerts.append({
                    "node_id": node_id,
                    "rule": "Rule_6",
                    "type": "TRACE_GAP",
                    "message": f"{node_id} (ADD) herhangi bir GDD (L1) veya VD (L0) gereksinimine bağlanmıyor."
                })
                rule_violations["Rule_6"] += 1

        # Rule 7: NDD -> VD Trace
        if level_cat == "L2":
            parents = adj_backward.get(node_id, [])
            vd_parents = [p for p in parents if p.startswith("REQ_VD_")]
            if not vd_parents:
                alerts.append({
                    "node_id": node_id,
                    "rule": "Rule_7",
                    "type": "TRACE_GAP",
                    "message": f"{node_id} (NDD) doğrudan bir REQ_VD_* (L0) gereksinimine bağlanmıyor."
                })
                rule_violations["Rule_7"] += 1

        # Rule 8: PBI -> L3 Trace
        if level_cat == "L4":
            parents = adj_backward.get(node_id, [])
            l3_parents = [p for p in parents if p.startswith("REQ_TDD_") or p.startswith("REQ_ADD_")]
            if not l3_parents:
                alerts.append({
                    "node_id": node_id,
                    "rule": "Rule_8",
                    "type": "TRACE_GAP",
                    "message": f"{node_id} (PBI) herhangi bir Teknik (TDD) veya Sanat (ADD) gereksinimine bağlanmıyor."
                })
                rule_violations["Rule_8"] += 1

        # Rule 9: QA -> PBI Link
        if level_cat == "L5":
            parents = adj_backward.get(node_id, []) + adj_forward.get(node_id, [])
            pbi_links = list(set([p for p in parents if p.startswith("PBI")]))
            if len(pbi_links) != 1:
                alerts.append({
                    "node_id": node_id,
                    "rule": "Rule_9",
                    "type": "LINK_ERROR",
                    "message": f"{node_id} (Test Case) tam olarak 1 adet PBI ile ilişkili olmalıdır (Bulunan bağ sayısı: {len(pbi_links)})."
                })
                rule_violations["Rule_9"] += 1

        # Rule 10: QA -> L3 Link
        if level_cat == "L5":
            if not has_path_to_level(node_id, "L3-C", adj_backward, nodes) and not has_path_to_level(node_id, "L3-D", adj_backward, nodes):
                alerts.append({
                    "node_id": node_id,
                    "rule": "Rule_10",
                    "type": "LINK_ERROR",
                    "message": f"{node_id} (Test Case) dolaylı veya doğrudan herhangi bir L3 (TDD/ADD) teknik şartnamesine ulaşamıyor."
                })
                rule_violations["Rule_10"] += 1

    # Health score calculations
    total_violations = sum(rule_violations.values())
    total_checks = len(nodes) * 4 # Max check load
    if total_checks > 0:
        health_score = max(0.0, min(100.0, 100.0 - (total_violations / total_checks) * 100.0 * 5))
    else:
        health_score = 100.0
        
    health_score = round(health_score, 1)

    # Coverage Matrix calculations
    # Map L0 nodes (rows) vs other nodes L1-L5 (columns) to check reachability
    coverage_matrix = {}
    l0_nodes = [nid for nid in nodes if nid.startswith("REQ_VD_")]
    other_nodes = [nid for nid in nodes if not nid.startswith("REQ_VD_")]
    
    for l0 in l0_nodes:
        coverage_matrix[l0] = {}
        for other in other_nodes:
            # Check if 'other' has an upward path to 'l0'
            has_path = has_path_to_node(other, l0, adj_backward)
            coverage_matrix[l0][other] = "LINKED" if has_path else "MISSING"

    stats = {
        "total_nodes": len(nodes),
        "total_edges": len(edges),
        "total_violations": total_violations,
        "violations_breakdown": rule_violations,
        "test_summary": {
            "PASS": list(test_statuses.values()).count("PASS"),
            "FAIL": list(test_statuses.values()).count("FAIL"),
            "UNTESTED": list(test_statuses.values()).count("UNTESTED")
        }
    }

    return {
        "alerts": alerts,
        "stats": stats,
        "health_score": health_score,
        "coverage_matrix": coverage_matrix
    }
