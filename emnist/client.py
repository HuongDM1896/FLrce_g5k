# This version gives more retries. let clients try to connect to server 10 times

import flwr as fl
from fedprox import fedprox_client_fn
from fedcom import fedcom_client_fn
from FLrce import FLrce_client_fn
import random
import numpy as np
import torch
import os
import time
import grpc

# --- set global seed cho client ---
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
torch.cuda.manual_seed_all(SEED)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False
os.environ["PYTHONHASHSEED"] = str(SEED)
# -------------------------------

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        print("Usage: python client.py <client_id> <server_IP> <clienttype>")
        sys.exit(1)
    
    cid = sys.argv[1]
    server_address = sys.argv[2]
    client_type = sys.argv[3]
    
    if client_type == "fedprox":
        client = fedprox_client_fn(cid)
    elif client_type == "fedcom":
        client = fedcom_client_fn(cid)
    elif client_type == "flrce":
        client = FLrce_client_fn(cid)
    else:
        raise ValueError(f"Unknown client type: {client_type}")

    # --- Retry loop for Flower client ---
    MAX_RETRIES = 10
    attempt = 0

    while attempt < MAX_RETRIES:
        try:
            print(f"[Client {cid}] Connecting to server ({attempt+1}/{MAX_RETRIES})...")
            fl.client.start_client(
                server_address=server_address,
                client=client,
                grpc_max_message_length=1024*1024*1024
            )
            print(f"[Client {cid}] finished successfully.")
            break  # success out loop
        except grpc.RpcError as e:
            attempt += 1
            wait_time = 3
            # wait_time = random.randint(2, 5)  # tránh retry đồng loạt
            print(f"[Client {cid}] gRPC connection failed: {e}. Retry in {wait_time}s ({attempt}/{MAX_RETRIES})...")
            time.sleep(wait_time)
        except Exception as e:
            attempt += 1
            wait_time = 3
            print(f"[Client {cid}] Unexpected error: {e}. Retry in {wait_time}s ({attempt}/{MAX_RETRIES})...")
            time.sleep(wait_time)
    else:
        print(f"[{cid}] Max retries reached. Exiting client.")
