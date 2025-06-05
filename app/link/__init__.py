from flask import Blueprint

bp = Blueprint('link', __name__)

from app.link import  routes