# Environment setup (on the machine that will run Super Odometry)
```bash
git clone https://github.com/water-horse/subt_localization_ws && cd subt_localization_ws
```
```bash
## Authentication is required to access the repository of Super Odometry.
wstool init && wstool merge dependencies.rosinstall && wstool update
```
```bash
cd operations
```
```bash
## Make sure there is no error running the following script.
## You may need to, for example, pip3 install bagpy.
python3 check_import.py
```
Put your sudo password in the file "passwd" in the current directory. Then,
```bash
cat passwd | sudo --stdin chmod 600 passwd
```
```bash
cat passwd | sudo --stdin whoami && sudo bash setup.bash
```
# Run Super Odometry locally
Under the "operations" folder, sepcify configurations in the file "config.json". See the **Configurations** section for detail. Then,
```bash
python3 driver_local.py --config config.json --mode MODE [--dataset-index INDEX]
```
MODE is 0 or 1, where 0 means SLAM mode and 1 means localization mode.  
  
INDEX is the index of the array of objects in the JSON file. If you don't specify this index, the driver will run all datasets one after another as specified in the JSON file. If you specify this index, the driver will only run the corresponding dataset.  
  
Everytime a dataset is to be processed, a Tmux terminal will pop up and will disappear when the dataset is finished. To kill the Python program without side effects, run the following script in a new terminal under the same folder **when there is a Tmux terminal alive**.
```bash
cat passwd | sudo --stdin bash escape.bash
```
Note: when all the datasets are finished, the Tmux terminal will not automatically disappear.
# Run Super Odometry on a remote machine via SSH
Make sure the steps in the **Environment setup** section is done on the remote machine. Then, on the local machine,
```bash
git clone https://github.com/water-horse/subt_localization_client && cd subt_localization_client
```
```bash
## Make sure there is no error running the following script.
python3 check_import.py
```
Put your sudo password in the file "userpasswd" in the current directory. Then,
```bash
cat userpasswd | sudo --stdin chmod 600 userpasswd
```
Put your SSH password in the file "sshpasswd" in the current directory. Then,
```bash
cat userpasswd | sudo --stdin chmod 600 sshpasswd
```
```bash
export SSH_HOST="username@ipaddress"
```
```bash
export SSH_WORKSPACE="/the/absolute/path/to/the/git/repo/on/the/remote/machine"
```
Sepcify configurations in the file "config.json". See the **Configurations** section for detail. Then,
```bash
python3 driver_remote.py --config config.json --mode MODE [--dataset-index INDEX]
```
MODE is 0 or 1, where 0 means SLAM mode and 1 means localization mode.  
  
INDEX is the index of the array of objects in the JSON file. If you don't specify this index, the driver will run all datasets one after another as specified in the JSON file. If you specify this index, the driver will only run the corresponding dataset.  
  
Everytime a dataset is to be processed, a Tmux terminal will pop up and will disappear when the dataset is finished. To kill the Python program without side effects, do the following in a new terminal under the same folder **when there is a Tmux terminal alive**.
```bash
export SSH_HOST="username@ipaddress"
```
```bash
export SSH_WORKSPACE="/the/absolute/path/to/the/git/repo/on/the/remote/machine"
```
```bash
bash escape.bash
```
Note: when all the datasets are finished, the Tmux terminal will not automatically disappear.  
Note: roscore runs on the port 11411 on the remote machine.
# Configurations
This section describes how to specify dataset configurations in the file "config.json". The fields in this JSON file are
- datapath
	> The absolute path of a folder where bag files of a single dataset are stored. This is a path on the machine that will run Super Odometry.
- namespace
	> Namespace here refers to the prefix of sensor topics in the bag files. For example, if there is a topic called "/cmu_rc7/imu/data" in the bag files, the namespace should be "cmu_rc7".
- dataconfig
	> The name of the file containing initial pose in the folder "subt_localization_ws/src/subt_state_estimation/super_odometry/config/dataset". Only the file name is needed here. The path to this file should not be included.
- cloudpath
	> The absolute path of the ground truth cloud on the machine that will run Super Odometry.
- outputpath
	> The absolute path of an existing folder where the results will be stored. This is a path on the machine that will run Super Odometry.
- start_time
	> This is the relative time in seconds to the beginning of bag files. The bag files will be played from this start time.
- end_time
	> This is the relative time in seconds to the beginning of bag files. The bag files will stop playing at this end time. If you want bag files to play to the end, set this field to -1.

When the driver is in SLAM mode, **dataconfig** and **cloudpath** have no effect on Super Odometry and they can be non-existing.  

It is recommended that **datapath**, **cloudpath** and **outputpath** share a long common path because this common path will be mapped to the docker container.  
