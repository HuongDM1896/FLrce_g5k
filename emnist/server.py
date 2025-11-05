import flwr as fl
from fedprox import fedprox_strategy
from fedcom import fedcom_strategy
from FLrce import FLrce_strategy
from FLrce_client import FLrce_client_manager
import random
import os
import numpy as np
import torch

def set_global_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    os.environ["PYTHONHASHSEED"] = str(seed)

set_global_seed(42)


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        print("Usage: python server.py <server_type>")
        sys.exit(1)
        
    server_type = sys.argv[1]
    FF = 0.1
    FE = 1.0
    MFC = 2  
    MEC = 2
    MAC = 2
    ROUNDS = 3

    test_acc = []
    selected_clients = []

    if server_type == "fedcom":
        strategy = fedcom_strategy(FF, FE, MFC, MEC, MAC, ACC=test_acc, ClientsSelection=selected_clients)
    if server_type == "fedprox":
        strategy = fedprox_strategy(FF, FE, MFC, MEC, MAC, ACC=test_acc, ClientsSelection=selected_clients)
    if server_type == "flrce":
        consensus = []
        cu = []
        hcp = []
        Inf = []
        earlystopping_records = []
        strategy = FLrce_strategy(FF, FE, MFC, MEC, MAC, accuracies=test_acc, ClientsSelection=selected_clients, ESCriteria=earlystopping_records)
    # randseed = random.randint(0, 99999)
    # random.seed(randseed)
    # Khởi động server
    fl.server.start_server(
        server_address="0.0.0.0:8080",  # hoặc IP thật của node server
        config=fl.server.ServerConfig(num_rounds=ROUNDS),
        strategy=strategy,
        client_manager=FLrce_client_manager()
    )
