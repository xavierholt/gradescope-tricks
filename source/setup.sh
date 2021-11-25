#! /bin/bash
set -e
set -x

apt-get update
apt-get install -y python3 python3-pip sudo valgrind
apt-get clean

pip3 install --no-cache gradescope-utils

useradd -MU student
