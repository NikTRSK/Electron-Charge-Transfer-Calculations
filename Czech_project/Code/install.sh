#!/bin/sh
PREREQS = "python python-dev perl python-pip"
echo "Installing Prerequisites"
apt-get update # pull latest packages from the repo
apt-get install -y $PREREQS

pip install numpy # install python numpy script