import argparse
import os
import rosbag

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=""
    )
    parser.add_argument("folder", help="")
    parser.add_argument("start_time", help="", type=float)
    parser.add_argument("end_time", help="", type=float)
    args = parser.parse_args()

    file_list = os.listdir(args.folder)
    file_list = sorted([file for file in file_list if file[-4:] == ".bag"])
    if len(file_list) == 0:
        print("ERROR")
        exit()
    if len(file_list) >= 2:
        file_list = [file_list[0], file_list[-1]]
    file_list = [os.path.join(args.folder, file) for file in file_list]

    abs_start_timestamp = rosbag.Bag(file_list[0], mode="r").get_start_time()
    start_timestamp = abs_start_timestamp + args.start_time
    if  args.end_time == -1:
        end_timestamp = rosbag.Bag(file_list[-1], mode="r").get_end_time()
    else:
        end_timestamp = abs_start_timestamp + args.end_time
    
    print(start_timestamp)
    print(end_timestamp)