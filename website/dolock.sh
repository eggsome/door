#!/bin/sh

# press the button and record the feedback
/usr/sbin/unlock-door; arecord -f S16_LE -r 44100 -d 3 /mnt/nvme/debian/root/test.wav

# run the audio comparison
chroot /mnt/nvme/debian /usr/bin/python3 /root/check_lock.py
EXIT_CODE=$?

if [ "$EXIT_CODE" -eq 10 ]; then
    # Whoops, we just locked the door! better press the button again to get to a locked state
    /usr/sbin/unlock-door
    logger DOOR: HOLD THE PHONE! We need to press the button again!
elif [ "$EXIT_CODE" -eq 11 ]; then
    # all good - audio check determined that the door is now correctly locked
    :
else
    # something is broken, let people know in the logs but take no other action
    logger DOOR: WARNING - Audio check failed.
fi

# remove test.wav because we've finished checking it
rm /mnt/nvme/debian/root/test.wav

# remove the busy file because we're finished
rm /tmp/door_busy
