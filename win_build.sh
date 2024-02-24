#!/bin/bash -xe

git clean -d -f -x .
test -d pyinstaller/windows

export PYTHON=/c/python38/python
export ROOT=$PWD

# make the .exe for the game
pyinstaller pyinstaller/windows/bonestorm.spec
