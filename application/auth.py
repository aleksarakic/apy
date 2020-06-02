from flask import Blueprint, url_for, request, abort, make_response
from .models import User, Calculation
from . import db

from werkzeug.security import check_password_hash

from flask import g, jsonify
from flask import current_app as app
from flask_httpauth import HTTPBasicAuth

authbp = Blueprint('authbp', __name__)
auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
        user = User.verify_auth_token(username_or_token)
        if not user:
            # try to authenticate with username/password
            user = User.query.filter_by(username = username_or_token).first()
            if not user or not user.verify_password(password):
                return False
        g.user = user
        return True


@authbp.route('/token', methods=['POST'])
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({ 'token': token.decode('ascii') })


@authbp.route('/users/<int:id>')
@auth.login_required
def get_user(id):
    """ 
    Finds User by it's ID
    and returns it's username 
    """
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'username': user.username})


@authbp.route('/signup', methods=['POST'])
def signup_post():
    """
    Creates user.
    json param example: {"username": "user", "password": "pass", "is_admin": "True" } 
    """
    username = request.json.get('username')
    password = request.json.get('password')
    is_admin = request.json.get('is_admin')

    if username is None or password is None:
        abort(make_response(jsonify("Invalid parameters"), 400))

    if User.query.filter_by(username=username).first(): # if a user is found, we want to redirect back to signup page so user can try again
        abort(make_response(jsonify("User already exists"), 400))
    
    admin = True if is_admin == True or is_admin == 'True' else False

    new_user = User(username=username, calculation_ids = [], is_admin = admin)
    new_user.hash_password(password)
    
    db.session.add(new_user)
    db.session.commit()

    return jsonify({ 'username': new_user.username }), 201, {'Location': url_for('get_user', id = new_user.id, _external = True)}