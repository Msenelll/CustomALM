import os
import re
from engine.ast_parser import ALL_TAGS_PATTERN, get_level

def get_level_rank(level_str):
    if "L0" in level_str: return 0
    if "L1" in level_str: return 1
    if "L2" in level_str: return 2
    if "L3-C" in level_str: return 3
    if "L3-D" in level_str: return 4
    if "L4" in level_str: return 5
    if "L5" in level_str: return 6
    return 99

def add_directed_edge(edges, t1, t2, edge_type="link"):
    if t1 == t2:
        return
        
    lvl1 = get_level(t1)
    lvl2 = get_level(t2)
    
    r1 = get_level_rank(lvl1)
    r2 = get_level_rank(lvl2)
    
    # We want upstream (lower rank number) -> downstream (higher rank number)
    if r1 < r2:
        source, target = t1, t2
    elif r2 < r1:
        source, target = t2, t1
    else:
        # Same level, preserve order of appearance
        source, target = t1, t2
        
    edge = {"source": source, "target": target, "type": edge_type}
    if edge not in edges:
        edges.append(edge)

def build_traceability_edges(docs_path, nodes, manual_edges=None):
    """
    Scans files a second time to establish edges using 4 trace strategies:
    1. Same Line Multi-Token
    2. Context Tracking (under heading of defined requirement)
    3. Reference Keywords (Ref:, Referans:, İlgili PBI:, vb.)
    4. Precondition Blocks (Giriş Ön Koşulları)
    """
    edges = []
    
    # Reference keywords list (case insensitive)
    ref_pattern = re.compile(
        r"(ref|referans|ilgili|ba\u011fl\u0131|\u00e7apraz\s*ba\u011f|cross\s*link|do\u011frular|link|on\s*kosul|\u00f6n\s*ko\u015ful)", 
        re.IGNORECASE
    )
    
    if not os.path.exists(docs_path):
        return edges

    # Find all md files
    md_files = []
    for root, dirs, files in os.walk(docs_path):
        for file in files:
            if file.endswith(".md"):
                md_files.append(os.path.join(root, file))

    for file_path in md_files:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        # Document-wide global upstreams scan (such as ## Giriş Ön Koşulları or Bağlı Olduğu lists near the top of the file)
        rel_path = os.path.relpath(file_path, docs_path).replace("\\", "/")
        local_tags = set(tag for tag, node in nodes.items() if node.get("file") == rel_path)
        
        global_upstreams = set()
        in_global_precondition = False
        
        for line in lines:
            line_strip = line.strip()
            # Detect section heading like ## Giriş Ön Koşulları or ## Ön Koşullar or Pre-requisites
            if re.search(r"^#+\s*(giri\u015f\s*|\u00f6n\s*)ko\u015fullar\u0131", line_strip, re.IGNORECASE) or "pre-requisite" in line_strip.lower():
                in_global_precondition = True
                continue
            elif line_strip.startswith("#"):
                in_global_precondition = False
                
            is_bağlı = re.search(r"ba\u011fl\u0131\s*oldu\u011fu", line_strip, re.IGNORECASE)
            
            if in_global_precondition or is_bağlı:
                found_tags = ALL_TAGS_PATTERN.findall(line_strip)
                for t in found_tags:
                    if t not in local_tags:
                        global_upstreams.add(t)
                        
        # Automatically connect all global upstreams to all local tags defined in this file
        for local_tag in local_tags:
            for g_up in global_upstreams:
                add_directed_edge(edges, g_up, local_tag, edge_type="precondition")

        current_context_tag = None
        in_precondition_block = False

        for idx, line in enumerate(lines):
            line_strip = line.strip()
            
            # Heading check to set context
            h_match = re.search(r"^(#+)\s*.*?(REQ_[A-Z0-9_]+|PBI_?[0-9]+|TC_QA_[A-Z0-9_]+)", line)
            if h_match:
                current_context_tag = h_match.group(2)
                in_precondition_block = False
                continue

            # Detect Precondition Block headers under active context
            if current_context_tag:
                if re.search(r"^(#+|\*|-)\s*(giri\u015f\s*|\u00f6n\s*)ko\u015fullar\u0131", line_strip, re.IGNORECASE):
                    in_precondition_block = True
                    continue
                # If we hit another major section, exit precondition block
                elif line_strip.startswith("#") or line_strip.startswith("---"):
                    in_precondition_block = False

            # Extract all tags in the line
            line_tags = ALL_TAGS_PATTERN.findall(line)
            
            # Strategy 1: Same Line Multi-Token
            if len(line_tags) >= 2:
                for i in range(len(line_tags)):
                    for j in range(i + 1, len(line_tags)):
                        add_directed_edge(edges, line_tags[i], line_tags[j], edge_type="multi-token")

            # Strategy 2 & 3 & 4: Under a parent context tag
            if current_context_tag and line_tags:
                for tag in line_tags:
                    if tag == current_context_tag:
                        continue
                        
                    # Strategy 4: Precondition Block
                    if in_precondition_block:
                        add_directed_edge(edges, tag, current_context_tag, edge_type="precondition")
                    # Strategy 3: Reference Keywords
                    elif ref_pattern.search(line_strip):
                        add_directed_edge(edges, tag, current_context_tag, edge_type="reference")
                    # Strategy 2: Simple contextual association
                    else:
                        add_directed_edge(edges, current_context_tag, tag, edge_type="context")

    # Merge manual edges if provided
    if manual_edges:
        for edge in manual_edges:
            src = edge.get("source")
            tgt = edge.get("target")
            etype = edge.get("type", "manual")
            if src and tgt:
                add_directed_edge(edges, src, tgt, edge_type=etype)

    return edges
