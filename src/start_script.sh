#!/bin/bash

# Start a new session
tmux new-session -d -s scripts

# Run redis-server in the first window
tmux send-keys -t scripts:0 'redis-server' C-m

# Sleep for 2 seconds
sleep 2

# Create a vertical split (two columns)
tmux split-window -h -t scripts:0

# In the left column, split horizontally three times for redis-server, redis-memory-remote, and dashboard.py
tmux split-window -v -t scripts:0.0
tmux send-keys -t scripts:0.1 './redis-memory-remote' C-m
tmux split-window -v -t scripts:0.1
tmux send-keys -t scripts:0.2 'python3 dashboard.py' C-m

# In the right column, split horizontally three times for the three other Python files
tmux select-pane -t scripts:0.3
tmux send-keys -t scripts:0.3 'python3 reality.py' C-m

tmux select-pane -t scripts:0.3
tmux split-window -v -t scripts:0.3
tmux send-keys -t scripts:0.4 'python3 frpCPU.py' C-m

tmux select-pane -t scripts:0.4
tmux split-window -v -t scripts:0.4
tmux send-keys -t scripts:0.5 'python3 inputReality.py' C-m

# Attach to the session
tmux attach -t scripts
