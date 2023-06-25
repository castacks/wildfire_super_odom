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
    parser.add_argument("--config", dest="config", help="JSON configuration file", required=True)
    parser.add_argument("--mode", dest="mode", help="0 for SLAM, 1 for localization", choices=["0", "1"], required=True)
    parser.add_argument("--dataset-index", dest="index", help="index of the dataset in the JSON configuration file to run", type=int, required=False)
    args = parser.parse_args()
    localization_mode = False if args.mode == "0" else True
    configs = json.load(open(args.config))
    if args.index != None:
        configs = [configs[args.index]]
    print("Configuration is")
    print(configs)

    for i in range(len(configs)):
        config = configs[i]
        file_list = os.listdir(config["datapath"])
        file_list = sorted([file for file in file_list if file[-4:] == ".bag"])
        assert len(file_list) > 0, "Number of bags in the data folder, \033[91m{}\033[0m should be non-zero".format(
            config["datapath"]
        )
        if len(file_list) >= 2:
            file_list = [file_list[0], file_list[-1]]
        file_list = [os.path.join(config["datapath"], file) for file in file_list]

        abs_start_timestamp = rosbag.Bag(file_list[0], mode="r").get_start_time()
        start_timestamp = abs_start_timestamp + config["start_time"]
        if  config["end_time"] == -1:
            end_timestamp = rosbag.Bag(file_list[-1], mode="r").get_end_time()
        else:
            end_timestamp = abs_start_timestamp + config["end_time"]
        
        if localization_mode:
            shared_path = os.path.commonpath([config["datapath"], config["cloudpath"], config["outputpath"]])
            docker_datapath = "/media/drive/" + os.path.relpath(config["datapath"], shared_path)
            docker_cloudpath = "/media/drive/" + os.path.relpath(config["cloudpath"], shared_path)
            docker_outputpath = "/media/drive/" + os.path.relpath(config["outputpath"], shared_path)
        else:
            shared_path = os.path.commonpath([config["datapath"], config["outputpath"]])
            docker_datapath = "/media/drive/" + os.path.relpath(config["datapath"], shared_path)
            docker_cloudpath = "/tmp"
            docker_outputpath = "/media/drive/" + os.path.relpath(config["outputpath"], shared_path)

        namespace = config["namespace"]
        if namespace[0] != "/":
            namespace = "/" + namespace
        if namespace[-1] == "/":
            namespace = namespace[:-1]
        
        if i + 1 < len(configs):
            proc = Process(target=escape_func, args=[math.ceil(end_timestamp - start_timestamp) + 60])
            proc.start()

        os.environ["IS_LOCALIZATION"] = args.mode
        os.environ["EXTERNAL_PATH"] = shared_path
        os.environ["DATA_PATH"] = docker_datapath
        os.environ["NAMESPACE"] = namespace
        os.environ["DATASET_CONFIG"] = config["dataconfig"]
        os.environ["CLOUD_PATH"] = docker_cloudpath
        os.environ["RESULT_PATH"] = docker_outputpath
        os.environ["START_TIME"] = str(config["start_time"])
        os.environ["PLAY_DELAY"] = "30" if localization_mode else "10"
        os.environ["PLAY_DURATION"] = "65536" if config["start_time"] == -1 else str(end_timestamp - start_timestamp)
        if localization_mode:
            os.environ["DURATION"] = str(math.ceil(end_timestamp - start_timestamp) + 40)

        os.system("tmuxp load tmux.yaml")

        if i + 1 == len(configs):
            break
        elif proc.is_alive():
            proc.terminate()
            stillClosing = True
            while stillClosing:
                stillClosing = False
                try:
                    proc.close()
                except ValueError:
                    stillClosing = True
            break
        else:
            proc.join()
            proc.close()

        os.environ.pop("MYVAR", None)
