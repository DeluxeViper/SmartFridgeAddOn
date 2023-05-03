#!/bin/bash

# file: stop_update_process.sh

SCRIPT_TO_EXECUTE="update_process.py"

OUTPUT_PID_FILE=update_process_running.pid

OUTPUT_PID_PATH=.

# If the .pid exists, read it & try to kill the process if it exists, then delete it.

the_pid=$(<$OUTPUT_PID_PATH/$OUTPUT_PID_FILE)

rm "$OUTPUT_PID_PATH/$OUTPUT_PID_FILE"

echo "Deleted $OUTPUT_PID_FILE file in $OUTPUT_PID_PATH dir"

kill "$the_pid"

COUNTER=1
# Kill all processes started by the update_process.py script
kill -9 `ps -ef | grep update_process.py | grep -v grep | awk '{print $2}'`

while [ -e /proc/$the_pid ]

do
   echo "$SCRIPT_TO_EXECUTE @: $the_pid is still running, counter: $COUNTER"
   
   sleep .7
   
   COUNTER=$[$COUNTER + 1]
   
   if [ $COUNTER -eq 5 ]; then
   
       kill -9 "$the_pid"
   fi
   
   if [ $COUNTER -eq 10 ]; then
   
       exit 1
   fi
done

echo "$SCRIPT_TO_EXECUTE @: $the_pid has finished"

echo "Killed all scripts started by the $SCRIPT_TO_EXECUTE.py script"
