import subprocess
import time
import os
import signal

# ----- CONFIG -----
BASE_DIR = "/home/mdo/FLrce_g5k/emnist"
SAVE_DIR = f"{BASE_DIR}/logs/flrce"

SERVER = "172.16.66.97"
CLIENTS = [
    "172.16.66.98",
    "172.16.66.99"
]

# ----- COMMON SETTINGS -----
PRE_CMD = "/usr/bin/python"  # Python interpreter
SERVER_SCRIPT = "server.py"
CLIENT_SCRIPT = "client.py"

SERVER_ARGS = "flrce"
CLIENT_ARGS_TEMPLATE = "{pid} {server}:8080 flrce"

# Ensure log directory exists
os.makedirs(SAVE_DIR, exist_ok=True)


# ==============================================================
# ============== CLEANUP FUNCTION ===============================
# ==============================================================

def cleanup_all(server_cmd: str, client_cmds: list):
    """Force kill Flower server/client processes across all nodes."""
    print("\n[Cleanup] Cleaning up all nodes ...")
    targets = [SERVER] + CLIENTS
    for node in targets:
        cmds = []
        cmds.append(f"pkill -f \"{server_cmd}\" >/dev/null 2>&1 || true")
        for cmd in client_cmds:
            cmds.append(f"pkill -f \"{cmd}\" >/dev/null 2>&1 || true")
        for cmd in cmds:
            full_cmd = f"ssh -T {node} '{cmd}'"
            subprocess.run(full_cmd, shell=True)
    print("[Cleanup] Done.\n")


# ==============================================================
# ============== RUN REMOTE FUNCTION ============================
# ==============================================================

def run_remote(host, cmd, log_file=None):
    """Execute a command on remote host via SSH."""
    redirect = f"> {log_file} 2>&1" if log_file else ""
    ssh_cmd = f"ssh -T {host} 'cd {BASE_DIR} && {cmd} {redirect}'"
    return subprocess.Popen(ssh_cmd, shell=True)


# ==============================================================
# ============== MAIN LAUNCH LOGIC ==============================
# ==============================================================

def main():
    print(f"[+] Launching Flower experiment from {BASE_DIR}\n")

    # ----- SERVER -----
    server_script_path = f"{BASE_DIR}/{SERVER_SCRIPT}"
    server_cmd = f"{PRE_CMD} {server_script_path} {SERVER_ARGS}"
    server_log = f"{SAVE_DIR}/server"

    print(f"[SERVER] Starting on {SERVER} ...")
    server_proc = run_remote(SERVER, server_cmd, server_log)
    time.sleep(5)  # Give server time to start

    # ----- CLIENTS -----
    client_cmds = []
    client_procs = []
    for pid, host in enumerate(CLIENTS):
        client_script_path = f"{BASE_DIR}/{CLIENT_SCRIPT}"
        client_args = CLIENT_ARGS_TEMPLATE.format(pid=pid, server=SERVER)
        client_cmd = f"{PRE_CMD} {client_script_path} {client_args}"
        client_cmds.append(client_cmd)

        client_log = f"{SAVE_DIR}/client_{pid}"
        print(f"[CLIENT {pid}] Starting on {host} ...")
        p = run_remote(host, client_cmd, client_log)
        client_procs.append(p)
        time.sleep(1)

    print("\nAll nodes launched.")
    print(f"Logs: {SAVE_DIR}")

    # ----- WAIT + CLEANUP -----
    try:
        # Wait for all clients to finish
        for p in client_procs:
            p.wait()
        print("[+] All clients finished.")

        # Wait for server to finish
        server_proc.wait()
        print("[+] Server finished.")

    except KeyboardInterrupt:
        print("\n[Interrupt] Ctrl+C detected, cleaning up...")
    finally:
        cleanup_all(server_cmd, client_cmds)


if __name__ == "__main__":
    main()
