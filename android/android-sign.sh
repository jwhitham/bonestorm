#!/bin/bash -xe
set -e

echo "Run this from the root of the repo"
test -f android/android-env-setup
source android/android-env-setup

jarsigner -keystore $HOME/keys/bonestorm/key.keystore \
    $BONESTORM/bonestorm-release-${BONESTORM_VERSION}.aab \
    upload-key
