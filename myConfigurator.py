import configparser

CONFIG_PATH = '/etc/httpd.conf'
MODE='DEV'

DEFAULT = {
    'ip': '0.0.0.0',
    'port': '80',
    'cpu_limit': '4',
    'thread_limit': '256',
    'max_connections': '1000',
    'document_root': '/var/www/html',
}

def config(path=CONFIG_PATH, mode=MODE):
    config = configparser.ConfigParser()
    try:
        config.read(path)
        ip = config[mode]['ip']
        port = config[mode]['port']
        cpu_limit = config[mode]['cpu_limit']
        root = config[mode]['document_root']
        max_connections = config[mode]['max_connections']

        return ip, int(port), int(cpu_limit), root, int(max_connections)

    except:
        config[mode] = DEFAULT

        with open(path, 'w') as configfile:
            config.write(configfile)

        return DEFAULT['ip'], int(DEFAULT['port']), int(DEFAULT['cpu_limit']), DEFAULT['document_root'], int(DEFAULT['max_connections'])