#!/bin/sh
# helper script to bring up the socket can interfaces manually

sudo modprobe peak_usb
sudo modprobe peak_pci
sudo ip link set can0 up type can bitrate 250000

sudo ip link set down can0
#ip link set down can2
sudo ip link set can0 type can bitrate 250000
#ip link set can2 type can bitrate 250000
sudo ip link set up can0
#ip link set up can2