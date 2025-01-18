#!/bin/sh

if [ -e "/tmp/door_busy" ]; then
    # a door lock or unlock attempt is already underway - warn the user
    cat /mnt/nvme/door_website/door_busy.content
    logger DOOR: Unlock requested, but service is busy
    exit 0
else
    # create lock file
    touch /tmp/door_busy
    # kick off scripts to lock the door
    ( nohup /usr/sbin/elevate_lock > /dev/null 2>&1 & ) &
    # let user know that their request is in progress
    cat /mnt/nvme/door_website/door_locking.content
    logger DOOR: Attempting to lock door
fi

