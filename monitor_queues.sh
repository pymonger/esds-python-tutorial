#!/bin/sh
clear
status=`sudo rabbitmqctl list_queues name messages_ready messages_unacknowledged`
while [ 1 ]; do
  echo "$status"
  sleep 1
  status=`sudo rabbitmqctl list_queues name messages_ready messages_unacknowledged`
  clear
done
