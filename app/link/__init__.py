from flask import Blueprint

link_bp = Blueprint('link', __name__)

from app.link import  routes