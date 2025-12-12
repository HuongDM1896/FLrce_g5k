import subprocess
import time
from datetime import datetime
import os, argparse
import socket

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
# Set up argument parser
parser = argparse.ArgumentParser(description="Run a benchmark experiment")
parser.add_argument("-m", "--fl", type=str, required=True, help="fl name (eg. flrce, fedcom, fedprox)")
parser.add_argument("-e", "--exp", type=str, required=True, help="Experiment name")
args = parser.parse_args()
OUTPUT = "Log"
FL = args.fl
EXP = args.exp


# ----- NEW BASE DIR FOR FLOWER -----
current_dir = os.getcwd() #Flrce/emnist
log_dir = os.path.join(current_dir, f"{OUTPUT}") #Flrce/emnist/Log
flower_log_dir = os.path.join(log_dir, f"flower_{EXP}", f"flower_{FL}") #Flrce/emnist/Log/Flower_exp/Flower_flrce/
SAVE_DIR = f"{flower_log_dir}/flwr_{timestamp}"  #Flrce/emnist/Log/Flower_exp/Flower_flrce/Flwr_time/

os.makedirs(SAVE_DIR, exist_ok=True)


with open("hostfile") as f:
    hosts = [l.strip() for l in f if l.strip()]

ips = [socket.gethostbyname(h) for h in hosts]
SERVER = ips[0]
CLIENTS = ips[1:]


# ----- COMMON SETTINGS -----
ADD = "GRPC_TRACE=all GRPC_VERBOSITY=DEBUG"
PRE_CMD = "/usr/bin/python"  # Python interpreter
SERVER_SCRIPT = "server.py"
CLIENT_SCRIPT = "client.py"

SERVER_ARGS = args.fl
CLIENT_ARGS_TEMPLATE = "{pid} {server}:8080 {fl}"



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
    ssh_cmd = f"ssh -T {host} 'cd {current_dir} && {cmd} {redirect}'"
    return subprocess.Popen(ssh_cmd, shell=True)


# ==============================================================
# ============== MAIN LAUNCH LOGIC ==============================
# ==============================================================

def main():
    print(f"[+] Launching Flower experiment from {current_dir}\n")

    # ----- SERVER -----
    server_script_path = f"{current_dir}/{SERVER_SCRIPT}"
    server_cmd = f"{PRE_CMD} {server_script_path} {SERVER_ARGS}"
    server_log = f"{SAVE_DIR}/server"

    print(f"[SERVER] Starting on {SERVER} ...")
    server_proc = run_remote(SERVER, server_cmd, server_log)
    time.sleep(5)  # Give server time to start

    # ----- CLIENTS -----
    client_cmds = []
    client_procs = []
    for pid, host in enumerate(CLIENTS):
        client_script_path = f"{current_dir}/{CLIENT_SCRIPT}"
        client_args = CLIENT_ARGS_TEMPLATE.format(pid=pid, server=SERVER, fl=FL)
        client_cmd = f"{PRE_CMD} {client_script_path} {client_args}"
        client_cmds.append(client_cmd)

        client_log = f"{SAVE_DIR}/client_{pid}"
        print(f"[CLIENT {pid}] Starting on {host} ...")
        p = run_remote(host, client_cmd, client_log)
        client_procs.append(p)
        time.sleep(0.5)

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

if __name__ == "__main__":
    main()
