# -*-coding:utf-8 -*-

from flask import request, current_app
from blog import db as mysql
import json, datetime, decimal


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


class Yrh:
    def __init__(self):
        self.db = 'blog2'

    def handle_requests(self, values):
        val_list = values.split(':')
        k = val_list[0]
        if len(val_list) == 2:
            v = val_list[1]
            # 判断传参类型，并转化
            v_type = int if v.isdigit() else str
            v = int(v) if v.isdigit() else str(v).decode('utf8')
            val = request.values.get(k, default=v, type=v_type)
        elif len(val_list) == 1:
            val = request.values.get(k, default='')
        return {k: val}

    def reqs(self, values):
        para = {}
        if type(values) == str:
            para.update(self.handle_requests(values))
            return para
        for value in values:
            para.update(self.handle_requests(value))
        return para

    def req(self, value):
        return request.values.get(value)

    def execute(self, sql, para=None, origin=False, db='blog2'):
        data = mysql.session.execute(sql, para, bind=mysql.get_engine(app=current_app, bind=db))
        # 取得原生结果
        if origin:
            return data
        # 判断是否查询
        if data.returns_rows:
            return [dict(r) for r in data]
        mysql.session.commit()
