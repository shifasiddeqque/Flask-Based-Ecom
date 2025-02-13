# app/extensions/migrate.py
from flask_migrate import Migrate

def init_migrate(app, db):
    migrate = Migrate(app, db)
