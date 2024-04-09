from flask import Blueprint
#main Blueprint
bp = Blueprint('main', __name__,url_prefix='/api/v1')
from app.main import routes
