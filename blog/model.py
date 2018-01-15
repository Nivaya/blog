# -*-coding:utf-8 -*-

from flask_login import UserMixin
from . import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import Table, Text
from markdown import markdown


class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, index=True)

    user = db.relationship('User', backref='user')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    username = db.Column(db.String(50), unique=True)
    password_hash = db.Column(db.String(100))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

    role = db.relationship('Role', backref='role')

    def __repr__(self):
        return '<User %r>' % self.username

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    # @password.setter
    # def password(self, password):
    #     self.password_hash = generate_password_hash(password)
    #
    # def verify_password(self, password):
    #     return check_password_hash(self.password_hash, password)


# 参考http://flask-login.readthedocs.io/en/latest/
# 用User.query.get(user_id)会报‘AnonymousUserMixin’错
@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=int(user_id)).first()


# 文章-标签 多对多
articles_tags = Table('articles_tags', db.Model.metadata,
                      db.Column('article_id', db.ForeignKey('article.id'), primary_key=True),
                      db.Column('tag_id', db.ForeignKey('tag.id'), primary_key=True)
                      )


class Article(db.Model):
    __tablename__ = 'article'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    body = db.Column(db.Text)
    description = db.Column(db.String(500))
    body_html = db.Column(db.Text)
    visited = db.Column(db.Integer, default=0)
    photo = db.Column(db.String(100))
    create_date = db.Column(db.DateTime, default=datetime.now)
    create_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    catalog_id = db.Column(db.Integer, db.ForeignKey('catalog.id'))
    recommand = db.Column(db.String(1))
    order_id = db.Column(db.Integer, default=0)

    create_user = db.relationship('User', backref='create_user', foreign_keys=create_user_id)
    catalogs = db.relationship('Catalog', backref='catalogs', foreign_keys=catalog_id)
    tags = db.relationship('Tag', secondary=articles_tags, backref='tags')

    def __repr__(self):
        return '<Article %r>' % self.title

    @staticmethod
    def on_body_changed(target, value, oldvalue, initiator):
        if value is None or value == '':
            target.body_html = ''
        else:
            target.body_html = markdown(value)


# 将markdown过的body保存到body_html
db.event.listen(Article.body, 'set', Article.on_body_changed)


class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(500))
    email = db.Column(db.String(100))
    create_user = db.Column(db.String(50))
    create_date = db.Column(db.DateTime, default=datetime.now)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'))

    comment_article = db.relationship('Article', backref='comment_article')

    def __repr__(self):
        return '<Comment %r>' % self.id


class Catalog(db.Model):
    __tablename__ = 'catalog'
    id = db.Column(db.Integer, primary_key=True)
    catalog = db.Column(db.String(30))
    catalog_eng = db.Column(db.String(30))

    def __repr__(self):
        return '<catalog %r>' % self.catalog


class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(30))

    articles = db.relationship('Article', secondary=articles_tags, backref='articles')

    def __repr__(self):
        return '<tag %r>' % self.tag
