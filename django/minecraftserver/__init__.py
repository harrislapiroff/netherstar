import docker


class MinecraftServer:
    eula_accepted = True
    broadcast_port = 25565
    rcon_port = 25575
    rcon_password = 'testing'


if __name__ == '__main__':
    mc = MinecraftServer()
    container = mc.start()
    import ipdb; ipdb.set_trace()
