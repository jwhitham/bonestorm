#!/bin/bash -xe

git clean -d -f -x .
test -d windows

export PYTHON=/c/python38/python
export ROOT=$PWD
export START=desktop.py

# make the .exe for the game
pyinstaller windows/bonestorm.spec
mv dist/bonestorm.exe .

# alternate version
export TARGET=/c/Users/jackd/OneDrive/Desktop
if test -d $TARGET
then
    export START=home.py
    pyinstaller windows/bonestorm.spec
    mv dist/bonestorm.exe $TARGET
fi
