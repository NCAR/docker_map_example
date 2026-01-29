from flask import Flask

app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates")

print("ROOT:", app.root_path)
print("STATIC:", app.static_folder)
print("TEMPLATES:", app.template_folder)

from app.main import views

from map_api.routes import map_blueprint
app.register_blueprint(map_blueprint)
