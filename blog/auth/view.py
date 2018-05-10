# -*-coding:utf-8 -*-
from flask import render_template, redirect, url_for, flash, g
from blog.form import LoginForm, RegisterForm
from flask_login import login_user, logout_user, login_required
from blog.model import User
from blog import db
from . import auth


# 登陆
@auth.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.lg_submit.data and login_form.validate_on_submit():
        user = User.query.filter_by(username=login_form.username.data).first()
        # 验证密码
        if user is not None and user.password_hash == login_form.password.data:
            login_user(user, login_form.remember.data)
            return redirect(url_for('content.index'))
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
# @auth.route('/register', methods=['GET', 'POST'])
def register():
    register_form = RegisterForm()
    if register_form.re_submit.data and register_form.validate_on_submit():
        user = User(username=register_form.username.data,
                    password_hash=register_form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('content.login', login_required=2))
    return render_template('login.html',
                           register_form=register_form,
                           para=g.para,
                           hots=g.hot_list,
                           links=g.links,
                           target='register')


# 登出
@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('content.index'))
