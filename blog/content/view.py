# -*-coding:utf-8 -*-
from flask import render_template, redirect, url_for, g
from blog.model import Article, Comment, articles_tags, Tag, Catalog
from blog import db
from blog.common.yrh import Yrh
from sqlalchemy import func
from . import content

yrh = Yrh()


# 标签云
def tags_cloud(catalog, keyword):
    tag_list = yrh.execute(u'''
                SELECT COUNT(t.tag) AS num,t.tag,:v_catalog catalog_eng FROM articles_tags at
                LEFT JOIN article a ON a.id = at.article_id
                LEFT JOIN catalog ca ON ca.id = a.catalog_id
                LEFT JOIN tag t ON t.id = at.tag_id
                WHERE ca.catalog_eng = :v_catalog or :v_catalog = 'search'
                AND (a.title like concat('%',:keyword,'%')  or :keyword = '')
                GROUP BY t.tag,:v_catalog''', {'v_catalog': catalog, 'keyword': keyword})
    return tag_list


# 主页
@content.route('/', methods=['GET', 'POST'])
@content.route('/index', methods=['GET', 'POST'])
def index():
    para = yrh.reqs(['page:1', 'url:index', 'title:最新发布'])
    sql_para = {'pagesize': g.pagesize,
                'nowcolumn': g.pagesize * (para['page'] - 1)}
    # 推荐文章列表
    recommands = db.session.query(Article.id, Article.title,
                                  (func.substr(Article.body, 1, 100) + '...').label('description')) \
        .filter(Article.recommand == 'Y').order_by(Article.order_id.desc(), Article.id.desc())
    # 所有文章列表
    articles = db.session.query(Article.id, Article.title, Article.visited, Article.create_date,
                                Catalog.catalog, Catalog.catalog_eng, Article.photo,
                                Article.order_id, func.count(Comment.id).label('counts'),
                                (func.substr(Article.body, 1, 100) + '...').label('description')) \
        .outerjoin(Comment) \
        .outerjoin(Catalog) \
        .filter(Article.hidden == None) \
        .group_by(Article.id) \
        .order_by(Article.order_id.desc(), Article.id.desc()) \
        .limit(sql_para['pagesize'])
    # 检查下一页行数
    rows_left = len(articles.offset(g.pagesize * para['page']).all())
    return render_template('index.html',
                           articles=articles.offset(sql_para['nowcolumn']),
                           recommands=recommands,
                           para=para,
                           hots=g.hot_list,
                           links=g.links,
                           left=rows_left)


# 分类/搜索列表
@content.route('/<catalog>', methods=['GET', 'POST'])
def catalog_list(catalog):
    addr = {'notes': u'IT笔记', 'info': u'资讯', 'search': u'搜索结果'}
    para = yrh.reqs(['page:1', 'keyword', 'tag'])
    para.update({'title': addr[catalog], 'url': catalog})
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
    articles = yrh.execute(sql, sql_para)
    # 检查下一页行数
    sql_para['nowcolumn'] = g.pagesize * para['page']
    rows_left = yrh.execute(sql, sql_para)
    return render_template('list.html',
                           articles=articles,
                           para=para,
                           hots=g.hot_list,
                           links=g.links,
                           tags=tags_cloud(catalog, para['keyword']),
                           left=len([dict(i) for i in rows_left]))


# 文章详情
@content.route('/detail/<int:id>', methods=['GET', 'POST'])
def detail(id):
    article = Article.query.get_or_404(id)
    cts = Comment.query.filter_by(article_id=id).count()
    para = yrh.reqs(['username', 'email', 'comment', 'comment_submit'])
    # 提交评论
    if para['comment_submit'] and para['username'] and para['comment']:
        comment = Comment(body=para['comment'],
                          create_user=para['username'],
                          email=para['email'],
                          article_id=id)
        db.session.add(comment)
        article.visited = article.visited - 1
        db.session.commit()
        return redirect(url_for('content.detail', id=article.id))

    article.visited = article.visited + 1
    db.session.commit()

    # 获取标签
    tags = db.session.query(Tag.tag).select_from(articles_tags) \
        .outerjoin(Article) \
        .outerjoin(Tag) \
        .filter(Article.id == id)
    # 获取评论
    comments = yrh.execute('''
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
