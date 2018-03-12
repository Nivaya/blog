# -*-coding:utf-8 -*-
from flask import render_template, redirect, url_for, flash, request, jsonify, g
from datetime import datetime
from .. import db
import json, os, datetime, decimal
from . import api


class Api:
    def __init__(self):
        pass

    @classmethod
    def reqs(cls, values):
        para = {}
        values = values.split(',')
        for value in values:
            val = request.values.get(value)
            para[value] = val if val else ''
        return para

    @staticmethod
    def encoder(obj):
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        return obj

    @classmethod
    def execute(cls, sql, para):
        data = db.session.execute(sql, para)
        data = [dict(i) for i in data]
        for row in data:
            for k, v in row.items():
                row[k] = cls.encoder(v)
        return data


@api.route('/api/test', methods=['GET'])
def test():
    para = Api.reqs('catalog,good,search,id')
    sql = u'''
        SELECT
            ag.id AS id,
            ag.name AS characteristic,
            ag.catalog_id AS categoryId,
            ag.price AS minPrice,
            'https://www.yaoronghua.top/static/uploads/lock_400x400.jpg' AS pic
        FROM
            api_goods ag
        LEFT JOIN api_catalog ac ON ac.id = ag.catalog_id
        WHERE 1=1
        and (:catalog = ac.name or :catalog = '')
        and (:good = ag.name or :good = '')
        and (:id = ag.id or :id = '')
        and (:search = ac.name or :search = ag.name or :search='')
    '''
    return jsonify(code=0, data=Api.execute(sql, para), msg='Success' if len(Api.execute(sql, para)) else 'Fail')


@api.route('/api/login', methods=['GET'])
def login():
    return jsonify(code=0, msg='can not get openid')


@api.route('/api/notice/list', methods=['GET'])
def notice():
    para = Api.reqs('id')
    sql = u'''
            SELECT date_format(dateadd,'%Y-%m-%d %H:%i:%S') dateAdd,id,isShow,title
            FROM api_notice an
            WHERE 1=1
            and (:id = an.id or :id = '')
        '''
    return jsonify(code=0, msg='success',
                   data={"totalRow": 1, "totalPage": 1, "dataList": Api.execute(sql, para)})


@api.route('/api/score/send/rule', methods=['GET'])
def score():
    para = Api.reqs('code')
    return jsonify(code=0, msg='success',
                   data=[{"code": para['code'] if para['code'] else '这里是你的code值', "codeStr": "好评送", "confine": 0.00,
                          "score": 3}])


@api.route('/api/banner/list', methods=['GET'])
def banner():
    para = Api.reqs('id')
    sql = u'''
            SELECT date_format(dateadd,'%Y-%m-%d %H:%i:%S') dateAdd,
            date_format(dateUpdate,'%Y-%m-%d %H:%i:%S') dateUpdate,
            id,linkUrl,paixu,picUrl,remark,status,statusStr
            FROM api_banner
            WHERE 1=1
            and (:id = id or :id = '')
        '''
    return jsonify(code=0, msg='success', data=Api.execute(sql, para))
