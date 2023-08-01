from flask import Flask
import app_config
from flask_session import Session  # https://pythonhosted.org/Flask-Session
from .views import _build_auth_code_flow
import os

SECRET_KEY = os.getenv("SECRET_KEY")

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config.from_object(app_config)
    Session(app)
    # This section is needed for url_for("foo", _external=True) to automatically
    # generate http scheme when this sample is running on localhost,
    # and to generate https scheme when it is deployed behind reversed proxy.
    # See also https://flask.palletsprojects.com/en/1.0.x/deploying/wsgi-standalone/#proxy-setups
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    app.jinja_env.globals.update(_build_auth_code_flow=_build_auth_code_flow)  # Used in template

    

    from .revenue import revenue
    from .views import home

    
    app.register_blueprint(revenue, url_prefix='/')
    app.register_blueprint(home, url_prefix='/')
    


    return app





