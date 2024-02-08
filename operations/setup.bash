# docker build -t twu3/super_odom:latest .

docker run --name super_odom --rm -itd -v `pwd`/..:/root/subt_ws twu3/super_odom:latest bash

docker exec -it super_odom bash -c "cd /root/subt_ws && source /opt/ros/melodic/setup.bash && catkin build"

docker stop super_odom
