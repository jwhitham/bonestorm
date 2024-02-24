#!/bin/bash -xe
set -e

echo "Run this from the root of the repo"
test -f android/android-env-setup
source android/android-env-setup

cd $BONESTORM
rm -f test-${BONESTORM_VERSION}.apks

java -jar $P4A_PACKAGES/bundletool-all-1.15.6.jar build-apks \
    --bundle=bonestorm-release-${BONESTORM_VERSION}.aab \
    --output=test-${BONESTORM_VERSION}.apks
java -jar $P4A_PACKAGES/bundletool-all-1.15.6.jar install-apks \
    --apks=test-${BONESTORM_VERSION}.apks 
