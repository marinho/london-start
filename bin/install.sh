#!/bin/sh
TEMP_PATH="/tmp"
#LONDON_START_PACKAGE="london-start" # Right address
LONDON_START_PACKAGE="-e git+git@github.com:mochii/london-start.git#egg=LondonStart" # Beta address

echo
echo "----------------------------------------------------------------------------------"
echo "| LondonStart Installer"
echo "|"
echo "| This script will install:"
echo "| "
echo "| > pip 1.1 (if necessary)"
echo "| > $LONDON_START_PACKAGE (with upgrade)"
echo "----------------------------------------------------------------------------------"
echo

# Checking pip installed
pip --version &> /dev/null
PIP_INSTALLED=$?

if (($PIP_INSTALLED));
then
    echo "Installing pip...";
    curl -s http://pypi.python.org/packages/source/p/pip/pip-1.1.tar.gz >$TEMP_PATH/pip-1.1.tar.gz
    cd $TEMP_PATH
    tar xvfz pip-1.1.tar.gz
    cd pip-1.1
    python setup.py install
    echo
fi

# Install london-start
pip install $LONDON_START_PACKAGE --upgrade
