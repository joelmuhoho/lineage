from flask import Blueprint

family_bp = Blueprint('family', __name__)

from app.family import routes