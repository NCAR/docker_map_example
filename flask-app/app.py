from flask import Flask
from map_api.routes import map_blueprint

def create_app():
    app = Flask(__name__)

    @app.route("/")
    def hello_world():
        return "Hello, World!"

    app.register_blueprint(map_blueprint, url_prefix="/map")

    return app

app = create_app()

