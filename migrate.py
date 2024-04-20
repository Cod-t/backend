from app import app,db
from flask_migrate import Migrate
with app.app_context():
    db.create_all()
    # migrate = Migrate(app, db)
    # migrate.init_app(app, db)

    # with app.app_context():
    #     migrate.upgrade(directory='migrations')
