# -*-coding:utf-8 -*-
from flask import Blueprint

content = Blueprint('content', __name__)

from . import view
