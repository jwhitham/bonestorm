#!/bin/bash -xe
set -e

echo "Run this from the root of the repo"
test -f android/android-env-setup
test -f ../venv/bin/activate
source android/android-env-setup
git clean -dfx .
cd $BONESTORM
PRIVATE=$BONESTORM/bonestorm

p4a aab --private=$PRIVATE \
    --package=com.jwhitham.bonestorm \
    --name="Bone Storm" \
    --version=$BONESTORM_VERSION \
    --bootstrap=sdl2 \
    --requirements=python3==3.10.13,hostpython3==3.10.13,cython,pygame \
    --blacklist-requirements=openssl \
    --orientation=portrait \
    --manifest-orientation=portrait \
    --icon=$PRIVATE/img/bone2.png \
    --presplash=$PRIVATE/img/splash.png \
    --storage-dir=$BONESTORM/p4a-storage \
    --dist_name=bonestorm \
    --arch=arm64-v8a \
    --arch=armeabi-v7a \
    --release
