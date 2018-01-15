# -*-coding:utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField, SubmitField
from flask_wtf.file import FileField
from wtforms.validators import DataRequired, EqualTo, ValidationError
from model import User
from flask_pagedown.fields import PageDownField


class LoginForm(FlaskForm):
    username = StringField(label=u'用户名', validators=[DataRequired()])
    password = PasswordField(label=u'密码', validators=[DataRequired()])
    remember = BooleanField(label=u'保持在线')
    lg_submit = SubmitField(u'登录')


class RegisterForm(FlaskForm):
    username = StringField(label=u'用户名', validators=[DataRequired()])
    password = PasswordField(label=u'密码', validators=[DataRequired()])
    confirm = PasswordField(label=u'确认密码',
                            validators=[DataRequired(), EqualTo('password', u'两次密码输入必须一致')])
    re_submit = SubmitField(u'马上注册')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(u'用户名已经被注册！')


class PostForm(FlaskForm):
    title = StringField(label=u'标题', validators=[DataRequired()])
    body = PageDownField(label=u'正文', validators=[DataRequired()])
    order = StringField(label=u'次序')
    photo = FileField(u'图片上传')
    po_submit = SubmitField(u'发表')
