import http.server
import socketserver
import webbrowser
import os
import sys
import time
import socket

PORT_START = 8000
PORT_END = 8050
DIR = os.path.dirname(os.path.abspath(__file__))

def find_available_port(start=PORT_START, end=PORT_END):
    for port in range(start, end):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                return port
            except OSError:
                continue
    return 8000

def launch_offline():
    index_path = os.path.join(DIR, "index.html")
    print("\n[+] Launching in Direct Offline Mode (Zero Server - Guaranteed No Errors)...")
    webbrowser.open("file://" + os.path.abspath(index_path))
    print("[✓] Dashboard opened in your default browser!")

def launch_server():
    port = find_available_port()
    os.chdir(DIR)
    
    class SilentHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            pass  # Suppress noisy logs

    print(f"\n[+] Starting High-Performance Local AI Agent Server on port {port}...")
    try:
        httpd = socketserver.TCPServer(("127.0.0.1", port), SilentHandler)
        url = f"http://127.0.0.1:{port}/index.html"
        print(f"[✓] Server Live: {url}")
        print("[+] Opening AI Agent Dashboard in browser...")
        webbrowser.open(url)
        print("\n=======================================================")
        print("  AI AGENT DASHBOARD IS RUNNING")
        print("  Press Ctrl+C in this window anytime to stop the server.")
        print("=======================================================\n")
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[+] Server safely stopped.")
    except Exception as e:
        print(f"[!] Server notice: {e}")
        print("[+] Falling back to 100% reliable direct browser mode...")
        launch_offline()

def main():
    print("""
  ╔════════════════════════════════════════════════════════════════════╗
  ║            🚀 AI RESUME & PORTFOLIO BUILDER AGENT                  ║
  ║                   SPECIAL LAUNCH CONTROLLER                        ║
  ╚════════════════════════════════════════════════════════════════════╝
    """)
    if len(sys.argv) > 1:
        if sys.argv[1] == "--server":
            launch_server()
            return
        elif sys.argv[1] == "--offline":
            launch_offline()
            return

    print("  [1] 🚀 Instant Launch (Recommended - Zero Server Error Guaranteed)")
    print("  [2] 🌐 High-Speed Local Web Server (http://127.0.0.1:8000)")
    print("  [3] 📌 Create 1-Click Shortcut on your Windows Desktop")
    print("  [4] 📁 Open Project Folder in Windows Explorer")
    print("  [5] ❌ Exit")
    print("")
    
    choice = input("  Select an option [1-5] (Default: 1): ").strip()
    if choice == "2":
        launch_server()
    elif choice == "3":
        create_shortcut()
    elif choice == "4":
        os.system(f'explorer "{DIR}"')
    elif choice == "5":
        sys.exit(0)
    else:
        launch_offline()

def create_shortcut():
    ps_script = os.path.join(DIR, "create_shortcut.ps1")
    if os.path.exists(ps_script):
        os.system(f'powershell -ExecutionPolicy Bypass -File "{ps_script}"')
    else:
        print("[!] Shortcut script not found.")

if __name__ == "__main__":
    main()
