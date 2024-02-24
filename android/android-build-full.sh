#!/bin/bash -xe
set -e

echo "Run this from the root of the repo"
test -f android/android-env-setup

# In case venv does not exist
mkdir -p ../venv/bin
touch ../venv/bin/activate

# Environment vars
source android/android-env-setup

# Cleanup working directories
rm -rf \
    "$P4A_STORAGE/build" \
    "$P4A_STORAGE/dists" \
    "$ANDROIDSDK" \
    "$ANDROIDNDK"

# Storage for packages used by p4a and pip (if not already present)
mkdir -p $BONESTORM/p4a-storage/packages

# Fetch Android NDK and SDK
cd "$P4A_PACKAGES"
wget -N https://dl.google.com/android/repository/android-ndk-r25b-linux.zip
wget -N https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip
wget -N https://github.com/google/bundletool/releases/download/1.15.6/bundletool-all-1.15.6.jar

# Extract NDK
cd "$P4A_STORAGE"
unzip -q $P4A_PACKAGES/android-ndk-r25b-linux.zip  

# Extract SDK command line tools
mkdir -p "$ANDROIDSDK"
cd "$ANDROIDSDK"
unzip -q $P4A_PACKAGES/commandlinetools-linux-11076708_latest.zip 

# Directory structure in the zip file doesn't match what p4a expects
ln -s cmdline-tools tools

export PATH=$ANDROIDSDK/cmdline-tools/bin:$PATH

# Fetch the rest of the SDK
sdkmanager --sdk_root="$ANDROIDSDK" "platforms;android-$ANDROIDAPI"
sdkmanager --sdk_root="$ANDROIDSDK" "build-tools;33.0.3"

# Now setup the Python venv and build tools
cd "$BONESTORM"

rm -rf venv
python -m venv venv
source venv/bin/activate

pi () {
    $BONESTORM/venv/bin/pip install \
        --cache-dir $BONESTORM/p4a-storage/packages \
        $1
}

pi appdirs==1.4.4
pi pyproject_hooks==1.0.0
pi packaging==23.2
pi build==1.0.3
pi toml==0.10.2
pi sh==1.14.3
pi MarkupSafe==2.1.5
pi colorama==0.3.3
pi jinja2==3.1.3
pi python-for-android==2024.1.21
pi Cython==3.0.8

# Now the build itself
cd "$BONESTORM/bonestorm"
git clean -dfx .
android/android-build.sh

