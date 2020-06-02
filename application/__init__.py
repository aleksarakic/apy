from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate = Migrate()
    # https://stackoverflow.com/questions/33944436

    with app.app_context():

        from .auth import auth

        from . import main

        from .auth import authbp as auth_blueprint
        app.register_blueprint(auth_blueprint)

        from .main import mainbp as main_blueprint
        app.register_blueprint(main_blueprint)

        from commands import requirements as requirements_blueprint
        app.register_blueprint(requirements_blueprint)

        from commands import terminate as terminate
        app.register_blueprint(terminate)

        from commands import seed as seed_blueprint
        app.register_blueprint(seed_blueprint)

        db.create_all()
        Migrate(app, db)

        return app