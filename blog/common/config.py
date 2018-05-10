# -*-coding:utf-8 -*-

# db参数
DB_INFO = {
    'blog2': {
        'user': 'root',
        'pwd': 'qq123456',
        'ip': 'localhost',
        'port': '3306'
    },
    # 'blog2': {
    #     'user': 'root',
    #     'pwd': '!QAZ2wsx',
    #     'ip': 'localhost',
    #     'port': '3306'
    # }
}

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

CONFIG = {
    'SECRET_KEY': 'strongaaa',
    'DEBUG': True,
    # 'SQLALCHEMY_ECHO': True,

    # 上传路径
    'UPLOAD_FOLDER': r'C:\Users\ronghuayao\PycharmProjects\blog\blog\static\uploads',
    # 'UPLOAD_FOLDER': '/www/blog/blog/static/uploads',

    'SQLALCHEMY_DATABASE_URI': 'mysql+mysqlconnector://{user}:{pwd}@{ip}:{port}/blog2'.format(**DB_INFO['blog2']),
    'SQLALCHEMY_BINDS': {
        'blog2': 'mysql+mysqlconnector://{user}:{pwd}@{ip}:{port}/blog2'.format(**DB_INFO['blog2'])
    },
    'SQLALCHEMY_TRACK_MODIFICATIONS': True,
    # 'SQLALCHEMY_COMMIT_ON_TEARDOWN': True,
}
