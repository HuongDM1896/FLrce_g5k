import flwr as fl
from fedprox import fedprox_client_fn
from fedcom import fedcom_client_fn
from FLrce import FLrce_client_fn
import random
import numpy as np
import torch
import os

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
    if len(sys.argv) == 3:
        print("Usage: python client.py <client_id> <server_IP> <clienttype>")
        sys.exit(1)
    
    cid = sys.argv[1]
    server_address = sys.argv[2]
    client_type = sys.argv[3]
    
    if client_type == "fedprox":
        client = fedprox_client_fn(cid)
        
    if client_type == "fedcom":
        client = fedcom_client_fn(cid)
        
    if client_type == "flrce":
        client = FLrce_client_fn(cid)
        
    # randseed = random.randint(0, 99999)
    # random.seed(randseed)
    fl.client.start_client(
            server_address=server_address,
            client=client,
            max_retries=3,
            max_wait_time=5
        )