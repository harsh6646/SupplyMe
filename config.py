import os
basedir = os.path.abspath(os.path.dirname(__file__))

WTF_CSRF_ENABLED = True
SECRET_KEY = "how-do-you-know"

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

TEMPLATES_AUTO_RELOAD = True
SQLALCHEMY_TRACK_MODIFICATIONS = True

# Auth
OAUTH_CREDENTIALS = {
    'facebook': {
        'id': '1204581086255705',
        'secret': 'f6b1ca0f9c3ce03c188818df85236f83'
    }
}
