from flask import Blueprint, url_for, request, abort, make_response
from .models import User, Calculation
from . import db

from werkzeug.security import check_password_hash

from flask import g, jsonify
from flask import current_app as app
from flask_httpauth import HTTPBasicAuth
import collections

mainbp = Blueprint('mainbp', __name__)

# variables used for in memory calculations. 
# consider moving to caching service 
array, calculations = [], []

auth = HTTPBasicAuth()

# TODO: remove to helper 
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


@app.before_request
def before_request():
    """ 
    set global variables if they are not
    already set.
    TODO: use caching service instead.
    """
    global array, calculations
    if request.endpoint == 'add' and not 'array' in globals() and not 'calculations' in globals():
        array, calculations = [], []


def flatten(x):
    """ Flattens multidimensional list """
    if isinstance(x, collections.Iterable):
        return [a for i in x for a in flatten(i)]
    else:
        return [x]

@app.route('/add', methods=['POST'])
@auth.login_required
def add():
    """
    adds an integer(s) to Array used for calculation.

    Parameters:
        integer(s): Integer or Array
        example: {"integer": [1,2,3] }
    """
    global array

    param = request.json.get('integer')
    if not param:
        abort(make_response(jsonify("Param is not valid"), 400))

    array.append(param)

    if isinstance(param, list):
        # catch exception
        array = flatten(array)

    return jsonify({'success': array}), 200
 


@app.route('/calculate', methods=['GET'])
# @auth.login_required
def calculate():
    """
    Calculates the sum of all elements that exist in the array, saves it and returns it.
    If parameter all is provided, then call returns all calculated sums

    Parameters:
        integer(s) : integer, Array
    """
    global calculations
    all_param = None
    try:
        all_param = request.json.get('all')
    except:
        pass

    if not array:
        abort(make_response(jsonify("Array for calculation is empty. #Add something"), 400))

    if all_param:
        return jsonify({'success': calculations}), 200
    
    summed = sum(array)
    calculations.append(summed)

    return jsonify({'success': summed}), 200


@app.route('/reset', methods=['POST'])
@auth.login_required
def reset():
    """
    Saves array and calculations, give it some ID, 
    and empties array and all calculations from memory
    """
    global array, calculations

    new_calculation = Calculation(array = array, calculations = calculations)
    db.session.add(new_calculation)
    db.session.flush()

    if g.user:
        g.user.calculation_ids.append(new_calculation.id)

    db.session.commit()

    del(array, calculations)
    return jsonify({'success': 'reseted'}), 200


@app.route('/history', methods=['GET'])
@auth.login_required
def history():
    """
    returns JSON object with previous calculations
    eg. [{“id”: 1, “array”: [16, 20, 4, 10], “calculations”: [36, 50]}])

    """
    id_param = None
    try:
        id_param = request.json.get('id')
    except:
        pass

    calculations = Calculation.query.all()

    user = g.user
    if user and not user.is_admin:
        calculations = db.session.query(Calculation).filter(Calculation.id.in_(g.user.calculation_ids)).all()

    if id_param:
        el = [el for el in calculations if el.id == id_param]
        if el:
            calculations = el
            [calculations]
        else:
            abort(make_response(jsonify("There is no Calculation with that ID"), 404))

    return jsonify([el.serialize() for el in calculations]), 200