"""
用于配置数据库等信息
是正式服务器的配置
"""
configs = {
    'debug': True,
    'db': {
        'host': '192.168.0.103',
        'port': 3306,
        'user': 'root',
        'password': '123456',
        'db': 'python'
    },
    'session': {
        'secret': 'Awesome'
    }
}
_COOKIE_KEY = configs['session']['secret']

print(_COOKIE_KEY)