from . import ENV, SECRET_KEY, PORT, FRONTEND_URL


def load_config(app):
    # GENERAL CONFIG
    app.config["ENV"] = ENV
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["PORT"] = PORT
    app.config['FRONTEND_URL'] = FRONTEND_URL
