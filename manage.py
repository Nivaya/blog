# -*-coding:utf-8 -*-
from flask_script import Manager, Shell
from livereload import Server
from blog import create_app, db
from blog.model import User
from blog.common.config import CONFIG
from flask_migrate import Migrate, MigrateCommand
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

app = create_app(CONFIG)
manager = Manager(app)


@manager.option('-h', '--host', help='Your host', dest='host', default='127.0.0.1')
@manager.option('-p', '--port', help='Your port', dest='port', default=5500)
def dev(host, port):
    """
    Test Mode
    """
    CONFIG['DEBUG'] = True
    app = create_app(CONFIG)
    server = Server(app.wsgi_app)
    server.watch('**/*.*')
    server.serve(host=host, port=int(port))


@manager.command
def run():
    """
    Product Rode
    """

    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(5500)
    IOLoop.instance().start()


def make_shell_context():
    return dict(app=app, db=db, User=User)


manager.add_command('db', MigrateCommand)
manager.add_command('shell', Shell(make_context=make_shell_context))

migrate = Migrate(app, db)

if __name__ == '__main__':
    manager.run()
