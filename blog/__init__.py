# -*-coding:utf-8 -*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_ckeditor import CKEditor
from flask_pagedown import PageDown
from blog.common.config import DB_INFO, CONFIG

db = SQLAlchemy()
bootstrap = Bootstrap()
ckeditor = CKEditor()
csrf = CSRFProtect()
pagedown = PageDown()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = '/index?login_required=1'
login_manager.login_message = u'请登录您的账户'
login_manager.login_message_category = 'error'


app = Flask(__name__)
app.config.update(CONFIG)

db.init_app(app)
bootstrap.init_app(app)
login_manager.init_app(app)
csrf.init_app(app)
ckeditor.init_app(app)
pagedown.init_app(app)

# 通用view
from blog import view

# 测试模块
from api import api

app.register_blueprint(api)

# 模块注册
from auth import auth as auth_bp
from content import content as content_bp
from post import post as post_bp

app.register_blueprint(auth_bp)
app.register_blueprint(content_bp)
app.register_blueprint(post_bp)
