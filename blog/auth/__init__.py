# -*-coding:utf-8 -*-
from flask import Blueprint

auth = Blueprint('auth', __name__, template_folder='.')

from . import view
