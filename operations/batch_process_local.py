import time
import os
import argparse
import json
import rosbag
import math
from multiprocessing import Process

def escape_func(sec_wait):
    time.sleep(sec_wait)
    os.system("cat passwd | sudo --stdin docker stop super_odom")
    os.system("tmux kill-session -t subt_localization")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Script for performing localization on a batch of datasets"
    )
    parser.add_argument("configuration_file", help="JSON configuration file")
    args = parser.parse_args()
    configs = json.load(open(args.configuration_file))
    print("EXTERNAL_PATH is")
    print(os.getenv("EXTERNAL_PATH"))
    print("Configuration is")
    print(configs)

    for config in configs:
        bagpath = os.getenv("EXTERNAL_PATH") + "/" + config["datapath"]
        file_list = os.listdir(bagpath)
        file_list = sorted([file for file in file_list if file[-4:] == ".bag"])
        assert len(file_list) > 0, "Number of bags in the data folder, \033[91m{}\033[0m should be non-zero".format(
            bagpath
        )
        if len(file_list) >= 2:
            file_list = [file_list[0], file_list[-1]]
        file_list = [os.path.join(bagpath, file) for file in file_list]

        abs_start_timestamp = rosbag.Bag(file_list[0], mode="r").get_start_time()
        start_timestamp = abs_start_timestamp + config["start_time"]
        if  config["end_time"] == -1:
            end_timestamp = rosbag.Bag(file_list[-1], mode="r").get_end_time()
        else:
            end_timestamp = abs_start_timestamp + config["end_time"]

        tmux_config = open("tmux.yaml.template", "r").read()
        namespace = config["namespace"]
        if namespace[0] == "/":
            namespace = namespace[1:]
        if namespace[-1] == "/":
            namespace = namespace[:-1]
        tmux_config = tmux_config \
            .replace("DATA_PATH", "/media/drive/" + config["datapath"]) \
            .replace("RESULT_PATH", "/media/drive/" + config["outputpath"]) \
            .replace("NAMESPACE", namespace) \
            .replace("OPTIONAL_DURATION", "" if config["start_time"] == -1 else "--duration " + str(end_timestamp - start_timestamp)) \
            .replace("DURATION", str(math.ceil(end_timestamp - start_timestamp) + 40)) \
            .replace("OPTIONAL_START_TIME", "" if config["start_time"] == 0 else "-s " + str(config["start_time"]))
        tmuxp_config_file = open("tmux.yaml", "w")
        tmuxp_config_file.write(tmux_config)
        tmuxp_config_file.close()

        ugv_config = open("ugv.yaml.template", "r").read()
        ugv_config = ugv_config \
            .replace("RESULT_PATH", "/media/drive/" + config["outputpath"])
        ugv_config_file = open("../src/subt_state_estimation/super_odometry/config/ugv.yaml", "w")
        ugv_config_file.write(ugv_config)
        ugv_config_file.close()

        ugv_launch = open("ugv_offline.launch.template", "r").read()
        ugv_launch = ugv_launch \
            .replace("CLOUD_PATH", "/media/drive/" + config["cloudpath"]) \
            .replace("DATASET_CONFIG", config["dataconfig"])
        ugv_launch_file = open("../src/subt_state_estimation/super_odometry/launch/ugv_offline.launch", "w")
        ugv_launch_file.write(ugv_launch)
        ugv_launch_file.close()

        proc = Process(target=escape_func, args=[math.ceil(end_timestamp - start_timestamp) + 90])
        proc.start()

        os.system("tmuxp load tmux.yaml")

        proc.join()

        os.system("rm tmux.yaml")