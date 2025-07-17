from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
import os
import sqlalchemy

app = Flask(__name__)


app.config["SECRET_KEY"] = "b6045a158d9860169419a83e9a798f8e"
if os.getenv("DATABASE_URL"):
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///NBL.db"

database = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
migrate = Migrate(app, database)
login_manager.login_view = "login_CriarConta"
login_manager.login_message_category = "alert-info"

from ComunidadeNBL import models
engine = sqlalchemy.create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
inspector = sqlalchemy.inspect(engine)
if not inspector.has_table("usuario"):
    with app.app_context():
        database.drop_all()
        database.create_all()
        print("Banco de dados criado com sucesso!")
else:
    print("Banco de dados já existe.")

from ComunidadeNBL import routes
