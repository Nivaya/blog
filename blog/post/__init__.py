# -*-coding:utf-8 -*-
from flask import Blueprint

post = Blueprint('post', __name__, template_folder='.')

from . import view
