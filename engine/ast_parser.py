import os
import re
import json
from datetime import datetime

# Regex patterns for requirement tokens
REQ_PATTERN = re.compile(r"REQ_[A-Z0-9_]+")
PBI_PATTERN = re.compile(r"PBI_?[0-9]+")
TC_PATTERN = re.compile(r"TC_QA_[A-Z0-9_]+")
ALL_TAGS_PATTERN = re.compile(r"(REQ_[A-Z0-9_]+|PBI_?[0-9]+|TC_QA_[A-Z0-9_]+)")

# Level classification based on prefix
def get_level(tag):
    if tag.startswith("REQ_VD_"):
        return "L0 (Vision)"
    elif tag.startswith("REQ_GDD_"):
        return "L1 (GDD)"
    elif tag.startswith("REQ_NDD_"):
        return "L2 (NDD)"
    elif tag.startswith("REQ_TDD_"):
        return "L3-C (TDD)"
    elif tag.startswith("REQ_ADD_"):
        return "L3-D (ADD)"
    elif tag.startswith("PBI_") or tag.startswith("PBI"):
        return "L4 (PBI)"
    elif tag.startswith("TC_QA_"):
        return "L5 (QA Test Case)"
    return "Unknown Level"

# Color codes for visual styling in Web UI
def get_color_class(level):
    if "L0" in level: return "level-l0"
    if "L1" in level: return "level-l1"
    if "L2" in level: return "level-l2"
    if "L3-C" in level: return "level-l3-tdd"
    if "L3-D" in level: return "level-l3-add"
    if "L4" in level: return "level-l4-pbi"
    if "L5" in level: return "level-l5-qa"
    return "level-unknown"

def get_module(tag):
    # Extract module identifier (e.g. REQ_GDD_CMB_01 -> CMB)
    parts = tag.split("_")
    if len(parts) >= 4:
        return parts[3]
    elif len(parts) == 3 and parts[0] == "REQ":
        return parts[2]
    return "GEN" # General/Generic

def parse_line_for_requirement(line, line_num, rel_path, nodes, lines):
    # Pattern A: Table Row definition
    # | **[REQ_VD_TEC_01]** | Ağ Yapısı | Detay... |
    table_match = re.search(r"\|\s*\*\*\[?(REQ_[A-Z0-9_]+|PBI_?[0-9]+|TC_QA_[A-Z0-9_]+)\]?\*\*\s*\|\s*([^|]+)\s*\|\s*([^|]+)", line)
    if table_match:
        tag = table_match.group(1).replace("[", "").replace("]", "").strip()
        title = table_match.group(2).strip().replace("**", "").replace("`", "")
        desc = table_match.group(3).strip()
        level = get_level(tag)
        nodes[tag] = {
            "id": tag,
            "title": title[:100],
            "desc": desc,
            "file": rel_path.replace("\\", "/"),
            "line": line_num,
            "level": level,
            "colorClass": get_color_class(level),
            "module": get_module(tag),
            "source": "auto",
            "timestamp": datetime.now().isoformat()
        }
        return True

    # Pattern B: Heading definition
    # ## 2.1. Kozmoloji [REQ_NDD_LOR_01]
    header_match = re.search(r"^(#+)\s*(.*?)(REQ_[A-Z0-9_]+|PBI_?[0-9]+|TC_QA_[A-Z0-9_]+)(.*)$", line)
    if header_match:
        tag = header_match.group(3).strip()
        title = header_match.group(2).strip().strip("[]:-. ")
        if not title:
            title = header_match.group(4).strip().strip("[]:-. ")
        
        # Capture description in next lines
        desc_lines = []
        for offset in range(1, 6):
            idx = line_num - 1 + offset
            if idx < len(lines):
                next_line = lines[idx].strip()
                if next_line.startswith("#") or next_line.startswith("|") or next_line.startswith("---"):
                    break
                if next_line:
                    desc_lines.append(next_line)
        desc = " ".join(desc_lines) if desc_lines else "Gereksinim detayları doküman içerisinde belirtilmiştir."
        level = get_level(tag)
        nodes[tag] = {
            "id": tag,
            "title": title[:100] if title else tag,
            "desc": desc,
            "file": rel_path.replace("\\", "/"),
            "line": line_num,
            "level": level,
            "colorClass": get_color_class(level),
            "module": get_module(tag),
            "source": "auto",
            "timestamp": datetime.now().isoformat()
        }
        return True

    # Pattern C: List Item or Bold definition
    # * **[REQ_TDD_CMB_01]** Title
    list_match = re.search(r"^\s*[\*\-]\s*\**\[?(REQ_[A-Z0-9_]+|PBI_?[0-9]+|TC_QA_[A-Z0-9_]+)\]?\**\s*(.*)$", line)
    if list_match:
        tag = list_match.group(1).strip()
        content = list_match.group(2).strip().strip("[]:-. ")
        parts = content.split(":")
        title = parts[0].strip() if len(parts) > 1 else tag
        desc = parts[1].strip() if len(parts) > 1 else content
        level = get_level(tag)
        nodes[tag] = {
            "id": tag,
            "title": title[:100],
            "desc": desc,
            "file": rel_path.replace("\\", "/"),
            "line": line_num,
            "level": level,
            "colorClass": get_color_class(level),
            "module": get_module(tag),
            "source": "auto",
            "timestamp": datetime.now().isoformat()
        }
        return True

    return False

def scan_file_for_nodes(file_path, base_dir, nodes):
    rel_path = os.path.relpath(file_path, base_dir)
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return

    for idx, line in enumerate(lines):
        line_num = idx + 1
        parse_line_for_requirement(line, line_num, rel_path, nodes, lines)

def parse_project_documents(docs_path, manual_req_path=None):
    """
    Recursively scans the docs_path directory for markdown documents,
    extracts requirements, and merges them with manual_requirements if present.
    """
    nodes = {}
    
    if not os.path.exists(docs_path):
        print(f"Docs path {docs_path} does not exist.")
        return nodes
        
    # Recursively find markdown files
    for root, dirs, files in os.walk(docs_path):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                scan_file_for_nodes(file_path, docs_path, nodes)
                
    # Merge manual requirements if they exist
    if manual_req_path and os.path.exists(manual_req_path):
        try:
            with open(manual_req_path, "r", encoding="utf-8") as f:
                manual_reqs = json.load(f)
                for tag, req in manual_reqs.items():
                    # Preserve/override attributes with "manual" source label
                    level = get_level(tag)
                    nodes[tag] = {
                        "id": tag,
                        "title": req.get("title", "Manuel Gereksinim"),
                        "desc": req.get("desc", ""),
                        "file": req.get("file", "manual_requirements.json"),
                        "line": req.get("line", 0),
                        "level": level,
                        "colorClass": get_color_class(level),
                        "module": get_module(tag),
                        "source": "manual",
                        "timestamp": req.get("timestamp", datetime.now().isoformat())
                    }
        except Exception as e:
            print(f"Error loading manual requirements: {e}")
            
    return nodes
