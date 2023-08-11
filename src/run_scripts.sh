#!/bin/bash

# Start a new tmux session named "scripts"
tmux new-session -d -s scripts 'python3 simulator.py'
tmux split-window -v -t
# Sleep for 1 second
sleep 1

tmux send 'python3 gas_rem_sender.py' ENTER
# Attach to the tmux session
tmux a

# Split the window vertically and run gas_rem_sender.py in the second pane
