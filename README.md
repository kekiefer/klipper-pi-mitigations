# klipper-pi-mitigations

A small (EXPERIMENTAL!) script to reduce latency jitter when running Klipper on a Raspberry Pi. It does three things:

- Sets the CPU governor to `performance` to avoid frequency scaling stalls
- Reduces dirty page writeback limits to reduce disk I/O latency spikes
- Applies `SCHED_RR` at priority 90 to the main klippy process and its named worker threads (the reactor and movement threads, not the logging threads)

## Installation

Make the script executable:

```bash
chmod +x /home/pi/klipper-pi-mitigations/bump-priorities.py
```

Install the included systemd drop-in, which adds the script as a post-start command on the Klipper service:

```bash
sudo mkdir -p /etc/systemd/system/klipper.service.d
sudo ln -sf /home/pi/klipper-pi-mitigations/klipper-mitigations.conf /etc/systemd/system/klipper.service.d/
sudo systemctl daemon-reload
sudo systemctl restart klipper
```
