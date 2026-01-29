from flask import Flask

app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates")

from app.main import views

from map_api.routes import map_blueprint
app.register_blueprint(map_blueprint)
