docker build -t twu3/super_odom:reallatest .

docker run --name super_odom -itd -v `pwd`/..:/root/subt_ws --rm twu3/super_odom:reallatest bash

docker exec -it super_odom bash -c "cd /root/subt_ws && source /opt/ros/melodic/setup.bash && catkin build"

docker stop super_odom
