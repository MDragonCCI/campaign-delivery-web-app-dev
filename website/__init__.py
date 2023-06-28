from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "AKJkfjdkalsfsadfasdf"
    

    from .revenue import revenue
    from .views import home

    
    app.register_blueprint(revenue, url_prefix='/')
    app.register_blueprint(home, url_prefix='/')


    return app





