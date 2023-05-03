#!/bin/bash

# file: start_update_process.sh

SCRIPT_TO_EXECUTE="update_process.py"

OUTPUT_PID_FILE=update_process_running.pid

OUTPUT_PID_PATH=.

# If the .pid file does not exist (let's assume no processes are running)...
# IF the .pid file does exist, then assume that the process is still running
if [ ! -e "$OUTPUT_PID_PATH/$OUTPUT_PID_FILE" ]; then

    # If .pid file doesnt exist, create it and start the python file and add the PID to it
    # Also log all output of the file to a log file, oL could be used here instead of oL
    stdbuf -o0 "python3" ./$SCRIPT_TO_EXECUTE > log 2>&1 & echo $! > "$OUTPUT_PID_PATH/$OUTPUT_PID_FILE"

    echo "Started $SCRIPT_TO_EXECUTE @ Process: $!"

    sleep .7

    echo "Created $OUTPUT_PID_FILE file in $OUTPUT_PID_PATH dir"
fi
exit 0