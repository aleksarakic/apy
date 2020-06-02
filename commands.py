import os
from flask import Blueprint

from application import db
from application.models import User, Calculation

requirements = Blueprint('requirements', __name__)

@requirements.cli.command('install')
def install():
    """ Installs requirements """
    print("Installing requirements")
    print("...")
    os.system("pip install -r requirements.txt")


terminate = Blueprint('terminate', __name__)

@terminate.cli.command('run')
def run():
    """ stops server """
    print("Server stops")
    print("...")
    os.system("kill $(ps aux | grep 'flask' | awk '{print $2}')")


seed = Blueprint('seed', __name__)

@seed.cli.command('run')
def run():
    """ Inserts data """
    # TODO: remove from commands!
    # create users
    regular_user = User(username='user', calculation_ids = [], is_admin = False)
    admin = User(username='admin', calculation_ids = [], is_admin = True)
    regular_user.hash_password('user')
    admin.hash_password('admin')
    
    # create calculations
    calc = Calculation(array = [16,20,4,10], calculations = [36,50])
    calc2 = Calculation(array = [4,10,4,10,4,10], calculations = [42])

    db.session.add(regular_user)
    db.session.add(admin)
    db.session.add(calc)
    db.session.add(calc2)

    db.session.flush()

    regular_user.calculation_ids.append(calc.id)
    admin.calculation_ids.append(calc2.id)

    db.session.commit()