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
echo "eula=true" > eula.txt
wget {minecraft_download_url}
java -jar {minecraft_filename} --initSettings
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
chown minecraft /var/minecraft/server/ -R
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
ExecStart=/var/minecraft/lib/jdk8/bin/java -jar /var/minecraft/server/{minecraft_filename}

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
ExecStart=/var/minecraft/lib/jdk8/bin/java -jar /var/minecraft/server/{forge_filename}

[Install]
WantedBy=multi-user.target
EOL
systemctl daemon-reload
"""


RUN_MINECRAFT = """
systemctl enable minecraft --now
"""


RUN_FORGE = """
systemctl enable minecraft --now
"""


FORGE_INSTALL_SCRIPT = "\n".join([
    SHEBANG,
    INSTALL_JDK8,
    INSTALL_MINECRAFT,
    INSTALL_FORGE,
    CREATE_SYSUSERS,
    CREATE_FORGE_SYSTEMD_UNIT,
    RUN_FORGE,
])


VANILLA_INSTALL_SCRIPT = "\n".join([
    SHEBANG,
    INSTALL_JDK8,
    INSTALL_MINECRAFT,
    CREATE_SYSUSERS,
    CREATE_MINECRAFT_SYSTEMD_UNIT,
    RUN_MINECRAFT,
])


def install_script_for_config(config):
    mc_version = config.version

    context = {
        'minecraft_download_url': mc_version.download_url,
        'minecraft_filename': mc_version.download_url.split('/')[-1],
    }

    if config.forge:
        forge_version = config.version.forge_version
        context.update({
            'forge_installer_url': forge_version.download_url,
            'forge_installer_filename': forge_version.download_url.split('/')[-1],
            # Can we deduce the filename with more confidence?
            'forge_filename': forge_version.download_url.split('/')[-1].replace('-installer', '')
        })
        return FORGE_INSTALL_SCRIPT.format(**context)

    return VANILLA_INSTALL_SCRIPT.format(**context)
