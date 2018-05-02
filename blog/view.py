# -*-coding:utf-8 -*-
from flask import render_template, redirect, url_for, flash, request, jsonify, g
from werkzeug.utils import secure_filename
from form import LoginForm, RegisterForm, PostForm
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from model import User, Catalog, Article, Comment, Tag, articles_tags, Link
from . import db
from . import ALLOWED_EXTENSIONS
import json, os, datetime, decimal, time


def init_views(app):
    class DataEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, datetime.datetime):
                return datetime.strftime(obj, '%Y-%m-%d %H:%M').replace(' 00:00', '')
            elif isinstance(obj, datetime.date):
                return datetime.strftime(obj, '%Y-%m-%d')
            elif isinstance(obj, decimal.Decimal):
                return str(obj)
            elif isinstance(obj, float):
                return round(obj, 8)
            return json.JSONEncoder.default(self, obj)

    @app.template_filter('eip_format')
    def eip_format(data):
        return json.dumps(data, json.dumps, cls=DataEncoder, ensure_ascii=False, indent=2)

    # 模板时间格式化
    @app.template_filter('dateformat')
    def dateformat(value, ft="%Y-%m-%d"):
        return value.strftime(ft)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html', title='Page Not Found', para={}), 404

    @app.errorhandler(Exception)
    def page_not_found(e):
        return render_template('404.html', title='Page Not Found', para={}), 404

    def log(func):
        def wrapper(*args, **kwargs):
            with open('blog.log', 'a') as f:
                f.write(time.strftime('%Y-%m-%d %H:%M:%S==>') + request.remote_addr + '\n')
            return func(*args, **kwargs)

        return wrapper

    @app.before_request
    @log
    def before_request():
        # 默认分页数
        g.pagesize = 8
        # 最新评论文章
        g.hot_list = db.session.execute('''
            SELECT COUNT(c.id) counts,a.id,a.title,a.visited,a.create_date,a.photo,max(c.create_date)
            FROM comment c
            LEFT JOIN article a ON c.article_id = a.id
            GROUP BY a.id
            ORDER BY max(c.create_date) DESC ''')
        g.links = db.session.execute('SELECT name,link,description FROM link ORDER BY order_id')
        g.user = current_user
        g.para = {'iflogin': request.args.get('login_required') or 'default'}
        # g.islogin = login()

    @app.teardown_request
    def teardown_request(exception):
        db.session.close()

    # 标签云
    def tags_cloud(catalog, keyword):
        tag_list = db.session.execute(u'''
                    SELECT COUNT(t.tag) AS num,t.tag,:v_catalog catalog_eng FROM articles_tags at
                    LEFT JOIN article a ON a.id = at.article_id
                    LEFT JOIN catalog ca ON ca.id = a.catalog_id
                    LEFT JOIN tag t ON t.id = at.tag_id
                    WHERE ca.catalog_eng = :v_catalog or :v_catalog = 'search'
                    AND (a.title like concat('%',:keyword,'%')  or :keyword = '')
                    GROUP BY t.tag,:v_catalog''', {'v_catalog': catalog, 'keyword': keyword})
        return tag_list

    # 主页
    @app.route('/', methods=['GET', 'POST'])
    @app.route('/index', methods=['GET', 'POST'])
    def index():
        para = {'page': request.args.get('page', 1, type=int),
                'url': 'index',
                'title': u'最新发布'}
        sql_para = {'pagesize': g.pagesize,
                    'nowcolumn': g.pagesize * (para['page'] - 1)}
        # 推荐文章列表
        recommand_sql = u'''
                    SELECT a.id,a.title,CONCAT(SUBSTR(a.body, 1, 100),'...') description
                    FROM article a
                    WHERE a.recommand='Y'
                    ORDER BY a.order_id DESC,a.id DESC'''
        recommands = db.session.execute(recommand_sql)
        # 所有文章列表
        sql = u'''
            SELECT a.id,a.title,CONCAT(SUBSTR(a.body, 1, 200),'...') description,a.visited,
                a.create_date,a.photo,cl.catalog,cl.catalog_eng,count(ct.id) AS counts,a.order_id
            FROM article a
            LEFT JOIN comment ct on ct.article_id = a.id
            LEFT JOIN catalog cl on cl.id = a.catalog_id
            WHERE a.hidden is null
            GROUP BY a.id
            ORDER BY a.order_id DESC,a.id DESC 
            LIMIT :pagesize OFFSET :nowcolumn'''
        articles = db.session.execute(sql, sql_para)
        # 检查下一页行数
        sql_para['nowcolumn'] = g.pagesize * para['page']
        rows_left = db.session.execute(sql, sql_para)
        return render_template('index.html',
                               articles=articles,
                               recommands=recommands,
                               para=para,
                               hots=g.hot_list,
                               links=g.links,
                               left=len([dict(i) for i in rows_left]))

    # 分类/搜索列表
    @app.route('/<catalog>', methods=['GET', 'POST'])
    def catalog_list(catalog):
        addr = {'notes': u'IT笔记', 'info': u'资讯', 'search': u'搜索结果'}
        para = {'page': request.args.get('page', 1, type=int),
                'keyword': request.args.get('keyword') or '',
                'tag': request.args.get('tag') or '',
                'title': addr[catalog],
                'url': catalog}
        sql_para = {'v_catalog': catalog,
                    'keyword': para['keyword'],
                    'tag': para['tag'],
                    'pagesize': g.pagesize,
                    'nowcolumn': g.pagesize * (para['page'] - 1)}
        sql = u'''
            SELECT a.id,a.title,CONCAT(SUBSTR(a.body, 1, 150),'...') description,a.visited,
                a.create_date,a.photo,cl.catalog,cl.catalog_eng,count(ct.id) AS counts,a.order_id
            FROM article a
            LEFT JOIN comment ct on ct.article_id = a.id
            LEFT JOIN catalog cl on cl.id = a.catalog_id
            LEFT JOIN  (SELECT ats.article_id id,tg.tag
                        FROM articles_tags ats
                        LEFT JOIN tag tg ON tg.id = ats.tag_id
                        where tg.tag = :tag or :tag = '') v on v.id = a.id
            WHERE (cl.catalog_eng = :v_catalog or :v_catalog = 'search')
            AND a.hidden is null
            AND (a.title like concat('%',:keyword,'%')  or :keyword = '')
            AND (v.tag = :tag or :tag = '')
            GROUP BY a.id
            ORDER BY a.order_id DESC,a.id DESC 
            {}'''.format('LIMIT :pagesize OFFSET :nowcolumn' if not para['keyword'] else '')
        articles = db.session.execute(sql, sql_para)
        # 检查下一页行数
        sql_para['nowcolumn'] = g.pagesize * para['page']
        rows_left = db.session.execute(sql, sql_para)
        return render_template('list.html',
                               articles=articles,
                               para=para,
                               hots=g.hot_list,
                               links=g.links,
                               tags=tags_cloud(catalog, para['keyword']),
                               left=len([dict(i) for i in rows_left]))

    # 文章详情
    @app.route('/detail/<int:id>', methods=['GET', 'POST'])
    def detail(id):
        article = Article.query.get_or_404(id)
        cts = Comment.query.filter_by(article_id=id).count()
        para = {'username': request.form.get('username'),
                'email': request.form.get('email'),
                'comment': request.form.get('comment'),
                'comment_submit': request.form.get('comment_submit')}
        # 提交评论
        if para['comment_submit'] and para['username'] and para['comment']:
            comment = Comment(body=para['comment'],
                              create_user=para['username'],
                              email=para['email'],
                              article_id=id)
            db.session.add(comment)
            article.visited = article.visited - 1
            db.session.commit()
            return redirect(url_for('detail', id=article.id))

        article.visited = article.visited + 1
        db.session.commit()

        # 获取标签
        tags = db.session.execute('''
            SELECT t.tag FROM articles_tags at
            LEFT JOIN article a ON a.id = at.article_id
            LEFT JOIN tag t ON t.id = at.tag_id
            WHERE at.article_id = :id''', {'id': id})
        # 获取评论
        comments = db.session.execute('''
            SELECT
                @rownum :=@rownum + 1 AS row_num,
                REPLACE (c.body, CHAR(10), '<br>') body_html,
                c.*
            FROM comment c,
                 (SELECT @rownum := 0) r
            where c.article_id = :id
            ORDER BY row_num DESC''', {'id': id})

        return render_template('detail.html',
                               article=article,
                               comments_count=cts,
                               comments=comments,
                               tags=tags,
                               hots=g.hot_list,
                               links=g.links,
                               para={'title': ''})

    # 登陆
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        login_form = LoginForm()
        if login_form.lg_submit.data and login_form.validate_on_submit():
            user = User.query.filter_by(username=login_form.username.data).first()
            # 验证密码
            if user is not None and user.password_hash == login_form.password.data:
                login_user(user, login_form.remember.data)
                return redirect(url_for('index'))
            flash(u'用户名或者密码错误！', 'error')
        # 注册成功时显示flash
        if g.para['iflogin'] == '2':
            flash(u'注册成功！现在您可以登录了', 'success')
        return render_template('login.html',
                               login_form=login_form,
                               hots=g.hot_list,
                               links=g.links,
                               target='login',
                               para={'title': ''})

    # 注册
    # @app.route('/register', methods=['GET', 'POST'])
    def register():
        register_form = RegisterForm()
        if register_form.re_submit.data and register_form.validate_on_submit():
            user = User(username=register_form.username.data,
                        password_hash=register_form.password.data)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login', login_required=2))
        return render_template('login.html',
                               register_form=register_form,
                               para=g.para,
                               hots=g.hot_list,
                               links=g.links,
                               target='register')

    # 登出
    @app.route('/logout', methods=['GET', 'POST'])
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('index'))

    # 发表文章
    @app.route('/write', methods=['GET', 'POST'])
    @app.route('/write/<int:id>', methods=['GET', 'POST'])
    @login_required
    def write(id=0):
        post_form = PostForm()
        # 标签
        tag_ids = []
        tagids = db.session.query(articles_tags).filter_by(article_id=id).all()
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
            post.title = request.form.get('title')
            post.catalog_id = request.form.get('catalog_id')
            post.body = request.form.get('body')
            post.recommand = request.form.get('recommand')
            post.order_id = request.form.get('order') or 0
            post_form.photo.data = post.photo
            if request.files['photo']:
                post.photo = request.form.get('title') + '-' + secure_filename(request.files['photo'].filename)
                upload_file(request.files['photo'], request.form.get('title'))

            # 标题、分类、链接图片必须有值
            if post.title and post.catalog_id and post.photo and post.body:
                db.session.add(post)
                db.session.commit()
                # 更新标签
                db.session.execute('delete from articles_tags where article_id=:id', {'id': id})
                id = db.session.execute('select max(id) from article').first()[0] if id == 0 else id
                for tag_id in request.values.getlist('tag_id'):
                    db.session.execute('''
                                    insert into articles_tags (article_id,tag_id) 
                                    value (:id,:tag_id)
                                ''', {'id': id, 'tag_id': tag_id})
                db.session.commit()
                return redirect(url_for('detail', id=post.id))
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
