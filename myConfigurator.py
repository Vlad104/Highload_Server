import configparser

CONFIG_PATH = '/etc/httpd.conf'

DEFAULT = {
    'ip': '0.0.0.0',
    'port': '80',
    'cpu_limit': '4',
    'thread_limit': '256',
    'max_connections': '1000',
    'document_root': '/var/www/html',
}

def config(path=CONFIG_PATH):
    config = configparser.ConfigParser()
    try:
        config.read(path)
        # ip = config[mode]['ip']
        # port = config[mode]['port']
        ip = '0.0.0.0'
        port = 80
        cpu_limit = config['cpu_limit']
        root = config['document_root']
        # max_connections = config['max_connections']
        max_connections = 10000

        return ip, int(port), int(cpu_limit), root, int(max_connections)

    except:
        return '0.0.0.0', 80, 4, '/var/www/html', 10000