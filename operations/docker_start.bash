XAUTH=/tmp/.docker.xauth
if [ ! -f $XAUTH ]
then
    touch $XAUTH
    xauth_list=$(xauth nlist :0 | sed -e 's/^..../ffff/')
    if [ ! -z "$xauth_list" ]
    then
        echo $xauth_list | xauth -f $XAUTH nmerge -
    else
        touch $XAUTH
    fi
    chmod a+r $XAUTH
fi

xhost +local:docker      

export EXTERNAL_PATH=/media/devansh/t7shield/lidar_processing

docker run --name super_odom -itd \
     --privileged \
     --gpus all \
     --ulimit core=-1 \
     -v `pwd`/..:/root/subt_ws/ \
     -v "$EXTERNAL_PATH:/media/drive" \
     -e DISPLAY=$DISPLAY  \
     -e QT_X11_NO_MITSHM=1 \
     -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
     -e XAUTHORITY=$XAUTH \
     -v $XAUTH:$XAUTH \
     --rm \
     --net host \
     twu3/super_odom:latest \
     bash
