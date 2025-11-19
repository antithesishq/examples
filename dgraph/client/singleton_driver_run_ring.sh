#!/bin/bash


pids=()

NODES=$(< node_count)

#create atomic counters, initialize to zero
for ((i = 0; i < NODES; i++));
do

COUNTER_FILE="/tmp/shared_counter_$i.bin"


dd if=/dev/zero of="$COUNTER_FILE" bs=8 count=1


done

export NUM_SWAPS_MAX=100001
export NUM_SWAPS_MIN=100000

RVAR=$(od -vAn -N1 -tu1 < /dev/urandom)
RVAR2=$((  ($RVAR % 3) + 1  ))

echo "Kicking off "$RVAR2" Processes"
for value in $(seq 1 "$RVAR2") #make random, maybe certain parallelisms cause issues
do
    #fire off parallel script w/ client
    /app/modify_ring.py &
    pids+=($!)  # Store PID of each background task
done


for pid in "${pids[@]}"; do
    wait $pid
done
