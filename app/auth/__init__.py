from flask import Blueprint
#auth BluePrint
bp = Blueprint('auth', __name__,url_prefix='/api/v1/auth')
from app.auth import auth_controller
