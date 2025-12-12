# python measure.py -m Net -e Exp -r 5

import expetator.experiment as experiment
from expetator.monitors import Mojitos, kwollect
# from expetator.leverages import Dvfs
import time, os, argparse
import platform

# Set up argument parser
parser = argparse.ArgumentParser(description="Run a benchmark experiment")
parser.add_argument("-m", "--fl", type=str, required=True, help="fl name")
parser.add_argument("-r", "--repeat", type=int, default=1, required=True, help="Number of repetitions (e.g., 2, the experiment will run twice)")
parser.add_argument("-e", "--exp", type=str, required=True, help="Experiment name")
args = parser.parse_args()
OUTPUT = "Log"
FL = args.fl
EXP = args.exp

def get_g5k_target_metric(cluster_name=None):
    if cluster_name is None:
        cluster_name = platform.node().split('-')[0]

    if cluster_name in ['grimani', 'grimoire', 'grimoire',
                        'gros', 'parasilo', 'paravance']:
        return 'pdu_outlet_power_watt'
    if cluster_name in ['troll', 'yeti', 'gemini', 'neowise', 'servan', 'sirius', 'paradoxe',
                        'orion', 'pyxis', 'sagittaire', 'taurus', 'nova', 'chirop', 'engelbourg','fleckenstein']:
        
        return 'wattmetre_power_watt'
    return 'bmc_node_power_watt'

kwollect.get_g5k_target_metric = get_g5k_target_metric

class flower:
    def __init__(self, params=["flower"]):
        self.names = {"flower"}
        self.params = params

    def build(self, executor):
        return {"flower": self.params}

    def run(self, bench, param, executor):
        before = time.time()
        cmd = f"python run_finish.py -e {EXP} -m {FL}"
        executor.local(cmd)
        return time.time() - before, "flower"

# Log directory

current_dir = os.getcwd() #Flrce/emnist
log_dir = os.path.join(current_dir, f"{OUTPUT}") #Flrce/emnist/Log
exp_log_dir = os.path.join(log_dir, f"flower_{EXP}", f"flower_{FL}", "Expetator") 
os.makedirs(exp_log_dir, exist_ok=True) ##Flrce/emnist/Log/flower_exp/flower_flname/Expetator_


if __name__ == "__main__":
    experiment.run_experiment(
            exp_log_dir,
            [flower()],
            leverages=[],
            # leverages= [Dvfs(frequencies=[1000000,1400000,1800000,2200000])], #gros
            monitors= [Mojitos(sensor_set={'user', 'rxp', 'dram0'}),
                kwollect.Power(metric=kwollect.get_g5k_target_metric())],
            times=args.repeat
            )
