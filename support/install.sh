#!/bin/sh

# Install the check_lan util that checks and handles the lan if it drops (until the pi firmware is fixed)
# need to crontab this for eg. every 2mins /2 * * * /opt/check_lan/check_lan
sudo mkdir /opt/check_lan
cp check_lan /opt/check_lan
