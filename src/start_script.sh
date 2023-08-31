#!/bin/bash

# Start a new session
tmux new-session -d -s scripts

# Run the first command in the first window
tmux send-keys -t scripts:0 'python3 reality.py' C-m

# Sleep for a bit
sleep 1

# Create a new pane and run the second command
tmux split-window -v -t scripts:0
tmux send-keys -t scripts:0.1 'python3 frpCPU.py' C-m

# Create another new pane and run the third command
# tmux split-window -h -t scripts:0
# tmux send-keys -t scripts:0.2 'python3 dashboard.py' C-m

# And so on for other commands

# Attach to the session
tmux attach -t scripts
