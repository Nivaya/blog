# -*-coding:utf-8 -*-
from flask import render_template, redirect, url_for, request, g
from werkzeug.utils import secure_filename
from blog.form import LoginForm, PostForm
from flask_login import login_required
from blog.model import Catalog, Article, Tag, articles_tags
from blog import db, app
from blog.common.yrh import Yrh
from blog.common.config import ALLOWED_EXTENSIONS
from blog.view import eip_format
from . import post
import os

yrh = Yrh()


# 发表文章
@post.route('/write', methods=['GET', 'POST'])
@post.route('/write/<int:id>', methods=['GET', 'POST'])
@login_required
def write(id=0):
    post_form = PostForm()
    # 标签
    tag_ids = []
    tagids = db.session.query(articles_tags).filter_by(article_id=id)
    for tagid in tagids:
        tag_ids.append(tagid[1])
    # 新增时
    if id == 0:
        # current_user._get_current_object()获取当前用户，只用current_user报错
        post = Article(create_user=g.user._get_current_object())
        page = {'catalog_id': '', 'id': id, 'tag_ids': tag_ids}
    # 修改时
    else:
        post = Article.query.get_or_404(id)
        post_form.body.data = post.body
        post_form.title.data = post.title
        post_form.order.data = post.order_id
        post_form.photo.data = post.photo
        page = {'catalog_id': post.catalog_id, 'id': id, 'tag_ids': tag_ids}
    # 提交内容
    if post_form.po_submit.data and post_form.validate_on_submit():
        post.title = yrh.req('title')
        post.catalog_id = yrh.req('catalog_id')
        post.body = request.form.get('body')
        post.recommand = yrh.req('recommand')
        post.order_id = yrh.req('order') or 0
        post_form.photo.data = post.photo
        if request.files['photo']:
            post.photo = yrh.req('title') + '-' + secure_filename(request.files['photo'].filename)
            upload_file(request.files['photo'], yrh.req('title'))

        # 标题、分类、链接图片必须有值
        if post.title and post.catalog_id and post.photo and post.body:
            db.session.add(post)
            db.session.commit()
            # 更新标签
            yrh.execute('delete from articles_tags where article_id=:id', {'id': id})
            id = yrh.execute('select max(id) from article', origin=True).first()[0] if id == 0 else id
            for tag_id in request.values.getlist('tag_id'):
                yrh.execute('''
                    insert into articles_tags (article_id,tag_id) 
                    value (:id,:tag_id)''', {'id': id, 'tag_id': tag_id})
            db.session.commit()
            return redirect(url_for('content.detail', id=post.id))
    title = u'添加新文章'
    if id > 0:
        title = u'编辑 - %s' % post.title
    # 如果没有修改也没有新增，回滚Post(author=g.user._get_current_object())
    db.session.rollback()
    return render_template('write.html',
                           title=title,
                           post_form=post_form,
                           post=post,
                           catalogs=Catalog.query,
                           tags=Tag.query,
                           login_form=LoginForm(),
                           hots=g.hot_list,
                           links=g.links,
                           page=eip_format(page),
                           para={'title': ''})


# 上传文件
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def upload_file(file, title):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], title + '-' + filename))
