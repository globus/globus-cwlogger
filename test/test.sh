#!/bin/bash

# tests install and functionality of globus-cwlogger
# assumes run as a user with sudo access

cd "$(dirname "$0")"

# get a branch to test or default to local repo
if [ $# -eq 1 ]
then
  branch=$1
  client_installpath="git+https://github.com/globus/globus-cwlogger@${branch}#subdirectory=client"
  daemon_installpath="git+https://github.com/globus/globus-cwlogger@${branch}#subdirectory=daemon"
else
  # default to local install
  client_installpath="../client/"
  daemon_installpath="../daemon/"
fi

set -ex

# cleanup any existing daemon or venv and (re)install as root
./_install_daemon.sh "$daemon_installpath"

# run client_test.py
virtualenv venv --python=python3
venv/bin/pip install "$client_installpath"
venv/bin/python client_test.py
rm -rf venv

# stop the daemon and run fail_test.py
sudo service globus_cw_daemon stop

virtualenv venv --python=python3
venv/bin/pip install "$client_installpath"
venv/bin/python fail_test.py
rm -rf venv
