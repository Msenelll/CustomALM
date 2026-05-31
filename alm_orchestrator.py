import os
import sys
import json
import argparse
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import socket
from datetime import datetime

# Add the root directory to path to import engine packages
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.project_manager import load_projects, save_projects, add_project, delete_project, update_project, scan_project
from engine.impact_analyzer import get_downstream_impact
from engine.baseline_manager import create_baseline, list_baselines, compare_baselines

# Paths configuration
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECTS_JSON = os.path.join(PROJECT_ROOT, "projects.json")
BASELINES_ROOT = os.path.join(PROJECT_ROOT, "baselines")
SYSTEM_UI_DIR = os.path.join(PROJECT_ROOT, "_LM_ALM_System")
OFFLINE_DATA_DIR = os.path.join(SYSTEM_UI_DIR, "alm_offline_data")
LIB_DIR = os.path.join(SYSTEM_UI_DIR, "lib")

class ALMRequestHandler(BaseHTTPRequestHandler):
    
    def log_message(self, format, *args):
        # Override to prevent logging clutter in output
        pass

    def send_json(self, data, status=200):
        try:
            response = json.dumps(data, indent=2, ensure_ascii=False).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(response)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(response)
        except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
            pass
        except Exception as e:
            print(f"Error sending JSON: {e}")

    def send_file(self, filepath, mime_type):
        if not os.path.exists(filepath):
            try:
                self.send_error(404, "File Not Found")
            except Exception:
                pass
            return
            
        try:
            with open(filepath, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', mime_type)
            self.send_header('Content-Length', str(len(content)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(content)
        except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
            # Client aborted or reset connection, ignore safely
            pass
        except Exception as e:
            # Sanitize exception message to strictly ASCII to prevent Latin-1 encoding crash
            safe_error_msg = str(e).encode('ascii', 'ignore').decode('ascii')
            try:
                self.send_error(500, f"Internal Server Error: {safe_error_msg}")
            except Exception:
                pass

    def do_OPTIONS(self):
        # Handle CORS pre-flight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        url_parsed = urllib.parse.urlparse(self.path)
        path = url_parsed.path
        
        # 1. Static Web Portal Routes
        if path == "/" or path == "/index.html":
            portal_path = os.path.join(SYSTEM_UI_DIR, "alm_portal.html")
            self.send_file(portal_path, "text/html; charset=utf-8")
            return
            
        elif path.startswith("/lib/"):
            filename = path.replace("/lib/", "")
            file_path = os.path.join(LIB_DIR, filename)
            # Simple mime type mapping
            mime = "application/javascript" if filename.endswith(".js") else "text/css"
            self.send_file(file_path, mime)
            return

        elif path.startswith("/alm_offline_data/"):
            filename = path.replace("/alm_offline_data/", "")
            file_path = os.path.join(OFFLINE_DATA_DIR, filename)
            self.send_file(file_path, "application/json; charset=utf-8")
            return

        # 2. API Endpoints
        elif path == "/api/health":
            self.send_json({"status": "ok", "message": "Ludus Magnus ALM backend online."})
            return

        elif path == "/api/projects":
            projects = load_projects(PROJECTS_JSON)
            self.send_json({"projects": projects})
            return

        elif path.startswith("/api/project/"):
            project_id = path.replace("/api/project/", "")
            projects = load_projects(PROJECTS_JSON)
            
            project_config = next((p for p in projects if p["id"] == project_id), None)
            if not project_config:
                self.send_json({"error": "Project not found"}, 404)
                return
                
            # Scan on demand or load cached data
            try:
                data = scan_project(project_id, project_config, OFFLINE_DATA_DIR)
                self.send_json(data)
            except Exception as e:
                self.send_json({"error": f"Error scanning project: {str(e)}"}, 500)
            return

        elif path.startswith("/api/impact/"):
            # Format: /api/impact/{project_id}/{node_id}
            parts = path.replace("/api/impact/", "").split("/", 1)
            if len(parts) != 2:
                self.send_json({"error": "Invalid arguments"}, 400)
                return
                
            project_id, node_id = parts
            projects = load_projects(PROJECTS_JSON)
            project_config = next((p for p in projects if p["id"] == project_id), None)
            
            if not project_config:
                self.send_json({"error": "Project not found"}, 404)
                return
                
            try:
                # Scan first to get latest nodes/edges
                data = scan_project(project_id, project_config, OFFLINE_DATA_DIR)
                impact = get_downstream_impact(node_id, data["nodes"], data["edges"])
                self.send_json(impact)
            except Exception as e:
                self.send_json({"error": f"Error running impact analyzer: {str(e)}"}, 500)
            return

        elif path.startswith("/api/baselines/"):
            project_id = path.replace("/api/baselines/", "")
            baselines = list_baselines(project_id, BASELINES_ROOT)
            self.send_json({"baselines": baselines})
            return

        elif path.startswith("/api/baseline-diff/"):
            # Format: /api/baseline-diff/{project_id}/{ts_a}/{ts_b}
            parts = path.replace("/api/baseline-diff/", "").split("/", 2)
            if len(parts) != 3:
                self.send_json({"error": "Invalid arguments"}, 400)
                return
                
            project_id, ts_a, ts_b = parts
            project_baselines_dir = os.path.join(BASELINES_ROOT, project_id)
            
            try:
                with open(os.path.join(project_baselines_dir, f"{ts_a}.json"), "r", encoding="utf-8") as f:
                    base_a = json.load(f)
                with open(os.path.join(project_baselines_dir, f"{ts_b}.json"), "r", encoding="utf-8") as f:
                    base_b = json.load(f)
                    
                diff = compare_baselines(base_a, base_b)
                self.send_json(diff)
            except Exception as e:
                self.send_json({"error": f"Error comparing baselines: {str(e)}"}, 500)
            return

        elif path.startswith("/api/export/"):
            # Format: /api/export/{project_id}/{format}
            parts = path.replace("/api/export/", "").split("/", 1)
            if len(parts) != 2:
                self.send_json({"error": "Invalid arguments"}, 400)
                return
                
            project_id, export_format = parts
            projects = load_projects(PROJECTS_JSON)
            project_config = next((p for p in projects if p["id"] == project_id), None)
            
            if not project_config:
                self.send_json({"error": "Project not found"}, 404)
                return
                
            try:
                data = scan_project(project_id, project_config, OFFLINE_DATA_DIR)
                if export_format == "json":
                    self.send_json(data["nodes"])
                elif export_format == "csv":
                    # Generate CSV response
                    csv_lines = ["ID,Title,Level,File,Line,Module,Source"]
                    for nid, node in data["nodes"].items():
                        title_clean = node["title"].replace('"', '""')
                        csv_lines.append(f'"{nid}","{title_clean}","{node["level"]}","{node["file"]}",{node["line"]},"{node["module"]}","{node["source"]}"')
                    csv_content = "\n".join(csv_lines).encode('utf-8')
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/csv; charset=utf-8')
                    self.send_header('Content-Length', str(len(csv_content)))
                    self.send_header('Content-Disposition', f'attachment; filename="{project_id}_requirements.csv"')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(csv_content)
                else:
                    self.send_json({"error": "Unsupported export format"}, 400)
            except Exception as e:
                self.send_json({"error": f"Error exporting requirements: {str(e)}"}, 500)
            return

        self.send_error(404, "Endpoint Not Found")

    def do_POST(self):
        url_parsed = urllib.parse.urlparse(self.path)
        path = url_parsed.path
        
        # Read payload
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else ""
        
        # Try parsing JSON if body exists
        body_json = {}
        if body:
            try:
                body_json = json.loads(body)
            except Exception as e:
                self.send_json({"error": f"Invalid JSON payload: {e}"}, 400)
                return

        if path == "/api/project":
            # Add project configuration
            required = ["id", "name", "local_root", "docs_path", "rules_path"]
            if not all(k in body_json for k in required):
                self.send_json({"error": f"Missing required parameters. Must include {required}"}, 400)
                return
                
            success, msg = add_project(PROJECTS_JSON, body_json)
            if success:
                self.send_json({"message": msg})
            else:
                self.send_json({"error": msg}, 400)
            return

        elif path == "/api/refresh":
            # Scan all projects
            projects = load_projects(PROJECTS_JSON)
            results = {}
            for p in projects:
                try:
                    scan_project(p["id"], p, OFFLINE_DATA_DIR)
                    results[p["id"]] = "success"
                except Exception as e:
                    results[p["id"]] = f"failed: {str(e)}"
            self.send_json({"message": "System refresh completed", "results": results})
            return

        elif path.startswith("/api/refresh/"):
            project_id = path.replace("/api/refresh/", "")
            projects = load_projects(PROJECTS_JSON)
            project_config = next((p for p in projects if p["id"] == project_id), None)
            
            if not project_config:
                self.send_json({"error": "Project not found"}, 404)
                return
                
            try:
                data = scan_project(project_id, project_config, OFFLINE_DATA_DIR)
                self.send_json({"message": f"Project {project_id} refreshed", "data": data})
            except Exception as e:
                self.send_json({"error": f"Failed to refresh project: {str(e)}"}, 500)
            return

        elif path.startswith("/api/git-sync/"):
            project_id = path.replace("/api/git-sync/", "")
            projects = load_projects(PROJECTS_JSON)
            project_config = next((p for p in projects if p["id"] == project_id), None)
            
            if not project_config:
                self.send_json({"error": "Project not found"}, 404)
                return
                
            try:
                data = scan_project(project_id, project_config, OFFLINE_DATA_DIR)
                self.send_json({"message": f"Git synchronized for {project_id}", "git": data["git"]})
            except Exception as e:
                self.send_json({"error": f"Git sync failed: {str(e)}"}, 500)
            return

        elif path.startswith("/api/baseline/"):
            project_id = path.replace("/api/baseline/", "")
            projects = load_projects(PROJECTS_JSON)
            project_config = next((p for p in projects if p["id"] == project_id), None)
            
            if not project_config:
                self.send_json({"error": "Project not found"}, 404)
                return
                
            try:
                label = body_json.get("label", "")
                data = scan_project(project_id, project_config, OFFLINE_DATA_DIR)
                result = create_baseline(project_id, label, data, BASELINES_ROOT)
                self.send_json({"message": "Baseline snapshot created", "baseline": result})
            except Exception as e:
                self.send_json({"error": f"Failed to create baseline: {str(e)}"}, 500)
            return

        self.send_error(404, "Endpoint Not Found")

    def do_PUT(self):
        url_parsed = urllib.parse.urlparse(self.path)
        path = url_parsed.path
        
        # Read payload
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else ""
        
        body_json = {}
        if body:
            try:
                body_json = json.loads(body)
            except Exception as e:
                self.send_json({"error": f"Invalid JSON payload: {e}"}, 400)
                return

        if path.startswith("/api/project/"):
            project_id = path.replace("/api/project/", "")
            success, msg = update_project(PROJECTS_JSON, project_id, body_json)
            if success:
                self.send_json({"message": msg})
            else:
                self.send_json({"error": msg}, 400)
            return
            
        self.send_error(404, "Endpoint Not Found")

    def do_DELETE(self):
        url_parsed = urllib.parse.urlparse(self.path)
        path = url_parsed.path
        
        if path.startswith("/api/project/"):
            project_id = path.replace("/api/project/", "")
            success, msg = delete_project(PROJECTS_JSON, project_id)
            if success:
                self.send_json({"message": msg})
            else:
                self.send_json({"error": msg}, 400)
            return
            
        self.send_error(404, "Endpoint Not Found")

def is_port_available(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return True
        except socket.error:
            return False

def start_server(port):
    # Dynamic port fallback if port is busy
    current_port = port
    while not is_port_available(current_port):
        print(f"Port {current_port} is busy. Trying fallback port {current_port + 1}...")
        current_port += 1
        
    server_address = ('localhost', current_port)
    httpd = HTTPServer(server_address, ALMRequestHandler)
    print(f"\n=======================================================")
    print(f"📡 Ludus Magnus Custom ALM Server running locally!")
    print(f"🔗 http://localhost:{current_port}/")
    print(f"=======================================================\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping ALM server.")
        httpd.server_close()

def run_scan_only():
    print("Executing single-run scan on all projects...")
    projects = load_projects(PROJECTS_JSON)
    for p in projects:
        print(f"Scanning project {p['id']} ({p['name']})...")
        try:
            scan_project(p["id"], p, OFFLINE_DATA_DIR)
            print(f"Project {p['id']} successfully scanned and cached.")
        except Exception as e:
            print(f"Failed to scan {p['id']}: {e}")

def run_baseline_only(label):
    print(f"Creating a baseline snapshot with label: '{label}'...")
    projects = load_projects(PROJECTS_JSON)
    for p in projects:
        try:
            data = scan_project(p["id"], p, OFFLINE_DATA_DIR)
            result = create_baseline(p["id"], label, data, BASELINES_ROOT)
            print(f"Baseline created for {p['id']}: {result}")
        except Exception as e:
            print(f"Failed to create baseline for {p['id']}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ludus Magnus Custom ALM Engine & Server Launcher")
    parser.add_argument("--serve", action="store_true", help="Start the local HTTP web portal server")
    parser.add_argument("--port", type=int, default=8002, help="Custom server port (default: 8002)")
    parser.add_argument("--scan", action="store_true", help="Run a single scan over all projects and export offline JSON")
    parser.add_argument("--baseline", type=str, help="Create a baseline snapshot for all configured projects")
    
    args = parser.parse_args()
    
    # Run based on arguments
    if args.serve:
        start_server(args.port)
    elif args.scan:
        run_scan_only()
    elif args.baseline:
        run_baseline_only(args.baseline)
    else:
        # Default behavior: start server on default port 8002
        start_server(8002)
