# -*-coding:utf-8 -*-
from flask import request, g, render_template
from flask_login import current_user
from blog import db
from sqlalchemy import func
import time
import json
from blog.model import Link, Comment, Article
from blog.common.yrh import DataEncoder


def common_error(app):
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html', title='Page Not Found', para={}), 404

    @app.errorhandler(Exception)
    def page_not_found(e):
        return render_template('404.html', title='Page Not Found', para={}), 404


def common_view(app):
    def log(fc):
        def wrapper(*args, **kwargs):
            with open('blog.log', 'a') as f:
                f.write(time.strftime('%Y-%m-%d %H:%M:%S==>') + request.remote_addr + '\n')
            return fc(*args, **kwargs)

        return wrapper

    # 模板时间格式化
    @app.template_filter('dateformat')
    def dateformat(value, ft="%Y-%m-%d"):
        return value.strftime(ft)

    @app.template_filter('eip_format')
    def eip_format(data):
        return json.dumps(data, json.dumps, cls=DataEncoder, ensure_ascii=False, indent=2)

    @app.before_request
    @log
    def before_request():
        # 默认分页数
        g.pagesize = 8
        # 链接
        g.links = Link.query.order_by(Link.order_id)
        # 当前用户
        g.user = current_user
        # 最新评论文章
        g.hot_list = db.session \
            .query(func.count(Comment.id).label('counts'), Article.id, Article.title, Article.visited,
                   Article.create_date, Article.photo, func.max(Comment.create_date)) \
            .outerjoin(Article) \
            .group_by(Article.id) \
            .order_by(Comment.create_date.desc())
        # 全局para
        g.para = {'iflogin': request.args.get('login_required') or 'default'}

    @app.teardown_request
    def teardown_request(exception):
        db.session.close()
