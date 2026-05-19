#!/bin/env python3

import os
import sys
import time

def set_scaling_gov():
    try:
        os.system(f'echo "performance" | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor')
        print(f"Set performance scaling governor")
    except Exception as e:
        print(f"Failed to set performance scaling governor")

def limit_disk_caching():
    try:
        os.system(f'echo 32768 | sudo tee /proc/sys/vm/dirty_background_bytes 32768')
        os.system(f'echo 131072 | sudo tee /proc/sys/vm/dirty_bytes')
        print(f"Limited disk cached size")
    except Exception as e:
        print(f"Failed to limit disk cache size")

def set_rt_priority(tid):
    try:
        os.system(f'sudo chrt -r -p 90 {tid}')
        print(f"Set real-time priority for thread {tid}")
    except Exception as e:
        print(f"Failed to set priority for thread {tid}: {e}")

def find_klippy_threads():
    # Iterate through all PIDs in /proc
    for pid in os.listdir('/proc'):
        if not pid.isdigit():
            continue
            
        try:
            # Read cmdline file
            cmdline_path = f'/proc/{pid}/cmdline'
            with open(cmdline_path, 'r') as f:
                cmdline = f.read().split('\0')
                
            # Check if klippy.py is in cmdline
            if any('klippy.py' in cmd for cmd in cmdline):
                klippy_pid = int(pid)
                print(f"Found Klippy process with PID: {klippy_pid}")
                
                # Set real-time priority for the main klippy process
                set_rt_priority(klippy_pid)

                # Iterate through task directory for threads
                task_dir = f'/proc/{klippy_pid}/task'
                for thread_id in os.listdir(task_dir):
                    if not thread_id.isdigit():
                        continue
                        
                    # Read thread status file to see if it has a name
                    status_path = f"{task_dir}/{thread_id}/status"
                    with open(status_path, 'r') as f:
                        status_content = f.read().split('\n')
                        for line in status_content:
                            if line.startswith("Name:"):
                                _, name = line.split(":", 1)
                                name = name.strip()
                                print(f"Thread {thread_id} - {name}")
                                # Set real-time priority for named threads, which are klippers queue and movement threads
                                if name != 'python':
                                    set_rt_priority(int(thread_id))
                                        
        except (IOError, OSError) as e:
            print(f"Could not access process {pid}: {e}")

if __name__ == "__main__":
    set_scaling_gov()
    limit_disk_caching()

    # HACK: need a better way to wait for klippy to start up before finding threads
    time.sleep(20)

    if len(sys.argv) > 1:
        pid = sys.argv[1]
        set_rt_priority(pid)
    else:
        find_klippy_threads()
