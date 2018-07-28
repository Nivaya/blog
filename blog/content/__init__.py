# -*-coding:utf-8 -*-
from flask import Blueprint

content = Blueprint('content', __name__, template_folder='.')

from . import view
