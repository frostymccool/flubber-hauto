#!/bin/sh
# kick off script
# params:
#    1 to kick of the xap-hub
#    2 to kick of heating controller


cd /home/common/heating

if [ "$1" = "1" ]; then
    echo "kick off hub"
    ./xap-hub &
fi

if [ "$1" = "2" ]; then
    echo "kick off heating controller"
    python xap_pollthermostats.py
fi

if [ "$1" = "3" ]; then
    echo "kick off both"
    ./xap-hub &
    python xap_pollthermostats.py
fi