SHEBANG = "#!/usr/bin/env bash"

INSTALL_JDK8 = """
mkdir -p /var/minecraft/lib
cd /var/minecraft/lib
wget https://github.com/AdoptOpenJDK/openjdk8-binaries/releases/download/jdk8u222-b10/OpenJDK8U-jdk_x64_linux_hotspot_8u222b10.tar.gz
mkdir jdk8
tar -xf OpenJDK8U-jdk_x64_linux_hotspot_8u222b10.tar.gz -C jdk8 --strip-components=1
export PATH=/var/minecraft/lib/jdk8/bin:$PATH
"""


INSTALL_MINECRAFT = """
mkdir -p /var/minecraft/server
cd /var/minecraft/server
wget {minecraft_download_url}

echo "eula=true" > eula.txt

cat >server.properties <<EOL
broadcast-rcon-to-ops=true
view-distance=10
max-build-height=256
server-ip=
level-seed=
rcon.port=25575
gamemode=survival
server-port=25565
allow-nether=true
enable-command-block=false
enable-rcon=false
enable-query=false
op-permission-level=4
prevent-proxy-connections=false
generator-settings=
resource-pack=
level-name=world
rcon.password=
player-idle-timeout=0
motd=A Minecraft Server
query.port=25565
force-gamemode=false
hardcore=false
white-list=false
broadcast-console-to-ops=true
pvp=true
spawn-npcs=true
generate-structures=true
spawn-animals=true
snooper-enabled=true
difficulty=easy
function-permission-level=2
network-compression-threshold=256
level-type=default
spawn-monsters=true
max-tick-time=60000
enforce-whitelist=false
use-native-transport=true
max-players=20
resource-pack-sha1=
spawn-protection=16
online-mode=true
allow-flight=false
max-world-size=29999984
EOL
"""


INSTALL_FORGE = """
wget {forge_installer_url}
java -jar {forge_installer_filename} --installServer
rm {forge_installer_filename}
"""


CREATE_SYSUSERS = """
mkdir -p /usr/lib/sysusers.d
echo 'u minecraft - "Minecraft Server User"' > /usr/lib/sysusers.d/minecraft.conf
systemd-sysusers
"""


CREATE_MINECRAFT_SYSTEMD_UNIT = """
cat >/etc/systemd/system/minecraft.service <<EOL
[Unit]
Description=Minecraft Server
StartLimitIntervalSec=0

[Service]
Type=simple
User=minecraft
Restart=always
WorkingDirectory=/var/minecraft/server/
ExecStart=/usr/bin/bash -c '/var/minecraft/lib/jdk8/bin/java -Xms{memory_size} -Xmx{memory_size} -jar /var/minecraft/server/{minecraft_filename}'

[Install]
WantedBy=multi-user.target
EOL
systemctl daemon-reload
"""


CREATE_FORGE_SYSTEMD_UNIT = """
cat >/etc/systemd/system/minecraft.service <<EOL
[Unit]
Description=Forge Server
StartLimitIntervalSec=0

[Service]
Type=simple
User=minecraft
Restart=always
WorkingDirectory=/var/minecraft/server/
ExecStart=/usr/bin/bash -c '/var/minecraft/lib/jdk8/bin/java -Xms{memory_size} -Xmx{memory_size} -jar /var/minecraft/server/{forge_filename} nogui'
[Install]
WantedBy=multi-user.target
EOL
systemctl daemon-reload
"""


FORGE_INSTALL_SCRIPT = "\n".join([
    SHEBANG,
    INSTALL_JDK8,
    INSTALL_MINECRAFT,
    INSTALL_FORGE,
    CREATE_SYSUSERS,
    CREATE_FORGE_SYSTEMD_UNIT,
])


VANILLA_INSTALL_SCRIPT = "\n".join([
    SHEBANG,
    INSTALL_JDK8,
    INSTALL_MINECRAFT,
    CREATE_SYSUSERS,
    CREATE_MINECRAFT_SYSTEMD_UNIT,
])


def install_script_for_config(config):
    mc_version = config.version

    context = {
        'minecraft_download_url': mc_version.download_url,
        'minecraft_filename': mc_version.download_url.split('/')[-1],
        'memory_size': '{}M'.format(config.droplet_size.memory)
    }

    if config.forge_version:
        forge_version = config.forge_version
        context.update({
            'forge_installer_url': forge_version.download_url,
            'forge_installer_filename': forge_version.download_url.split('/')[-1],
            # Can we deduce the filename with more confidence?
            'forge_filename': forge_version.download_url.split('/')[-1].replace('-installer', '*')
        })
        return FORGE_INSTALL_SCRIPT.format(**context)

    return VANILLA_INSTALL_SCRIPT.format(**context)


class Provisioner:
    def __init__(self, config, ip_address):
        pass
