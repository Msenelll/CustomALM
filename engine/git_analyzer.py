import subprocess
import re
import os
from engine.ast_parser import ALL_TAGS_PATTERN

def analyze_git_repo(project_root):
    """
    Scans the git repository at project_root to extract recent commits,
    extracts requirement tokens from commit messages, and lists branches.
    Fails gracefully if git is not available or if the directory is not a repo.
    """
    result = {
        "commits": [],
        "branches": [],
        "status": "idle",
        "error": None
    }
    
    if not os.path.exists(project_root):
        result["status"] = "path_not_found"
        result["error"] = "Project root path does not exist."
        return result

    # Check if git is installed and if it is a git repo
    try:
        # Run git status to verify it's a git repo
        check_git = subprocess.run(
            ["git", "status"], 
            cwd=project_root, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True, 
            shell=True
        )
        if check_git.returncode != 0:
            result["status"] = "no_git_repository"
            result["error"] = "Path is not a valid git repository or git command failed."
            return result
    except Exception as e:
        result["status"] = "git_command_missing"
        result["error"] = f"Failed to execute git command: {str(e)}"
        return result

    # Fetch last 150 commits
    try:
        # Format: hash|date(short)|commit_message
        git_log = subprocess.run(
            ["git", "log", "-n", "150", "--pretty=format:%h|%ad|%s", "--date=short"],
            cwd=project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True,
            encoding="utf-8",
            errors="ignore"
        )
        
        if git_log.returncode == 0 and git_log.stdout.strip():
            log_lines = git_log.stdout.strip().split("\n")
            for line in log_lines:
                parts = line.split("|", 2)
                if len(parts) == 3:
                    commit_hash, commit_date, commit_msg = parts
                    # Scan for tokens inside the commit message
                    tokens = list(set(ALL_TAGS_PATTERN.findall(commit_msg)))
                    result["commits"].append({
                        "hash": commit_hash,
                        "date": commit_date,
                        "msg": commit_msg,
                        "tokens": tokens
                    })
    except Exception as e:
        result["error"] = f"Error scanning commits: {str(e)}"

    # Fetch branches
    try:
        git_branches = subprocess.run(
            ["git", "branch", "-a"],
            cwd=project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True,
            encoding="utf-8",
            errors="ignore"
        )
        if git_branches.returncode == 0:
            branches = []
            for b_line in git_branches.stdout.strip().split("\n"):
                b_name = b_line.replace("*", "").strip()
                if b_name:
                    branches.append(b_name)
            result["branches"] = branches
    except Exception as e:
        if not result["error"]:
            result["error"] = f"Error scanning branches: {str(e)}"

    result["status"] = "success"
    return result
