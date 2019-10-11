FORGE_INSTALL_SCRIPT = """#!/usr/bin/env bash

mkdir -p /var/minecraft
cd /var/minecraft

wget https://github.com/AdoptOpenJDK/openjdk8-binaries/releases/download/jdk8u222-b10/OpenJDK8U-jdk_x64_linux_hotspot_8u222b10.tar.gz
mkdir jdk8
tar -xf OpenJDK8U-jdk_x64_linux_hotspot_8u222b10.tar.gz -C jdk8 --strip-components=1
export PATH=$PWD/jdk8/bin:$PATH

mkdir minecraft
cd minecraft
echo "eula=true" > eula.txt
wget {minecraft_download_url}
wget {forge_installer_url}

java -jar {minecraft_filename} --initSettings
java -jar {forge_installer_filename} --installServer
rm {forge_installer_filename}
java -jar {forge_filename}
"""

VANILLA_INSTALL_SCRIPT = """#!/usr/bin/env bash

mkdir -p /var/minecraft
cd /var/minecraft

wget https://github.com/AdoptOpenJDK/openjdk8-binaries/releases/download/jdk8u222-b10/OpenJDK8U-jdk_x64_linux_hotspot_8u222b10.tar.gz
mkdir jdk8
tar -xf OpenJDK8U-jdk_x64_linux_hotspot_8u222b10.tar.gz -C jdk8 --strip-components=1
export PATH=$PWD/jdk8/bin:$PATH

mkdir minecraft
cd minecraft
echo "eula=true" > eula.txt
wget {minecraft_download_url}

java -jar {minecraft_filename}
"""
