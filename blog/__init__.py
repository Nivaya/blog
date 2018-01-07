# -*-coding:utf-8 -*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_ckeditor import CKEditor
from flask_pagedown import PageDown

db = SQLAlchemy()
bootstrap = Bootstrap()
login_manager = LoginManager()
ckeditor = CKEditor()
csrf = CSRFProtect()
pagedown = PageDown()
login_manager.session_protection = 'strong'
login_manager.login_view = '/index?login_required=1'
login_manager.login_message = u'请登录您的账户'
login_manager.login_message_category = 'error'

UPLOAD_FOLDER = r'C:\Users\ronghuayao\PycharmProjects\blog\blog\static\uploads'
# UPLOAD_FOLDER = '/www/blog/blog/static/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


def create_app(db_info):
    app = Flask(__name__)
    app.secret_key = 'secury code122222223'
    app.debug = True
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://' + db_info + '/blog2'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    # app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

    db.init_app(app)
    bootstrap.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    ckeditor.init_app(app)
    pagedown.init_app(app)

    from .view import init_views
    init_views(app)
    return app
