import os
from flask import Flask
from app.routes import map_blueprint

# Explicitly tell Flask where static and templates are
app = Flask(
    __name__,
    static_folder=os.path.join(os.path.dirname(__file__), "app/static"),
    template_folder=os.path.join(os.path.dirname(__file__), "app/templates")
)
print("ROOT:", app.root_path)
print("STATIC:", app.static_folder)
print("TEMPLATES:", app.template_folder)
print(app.url_map)

#DATA_ROOT = Path("/output/model_predict")
DATA_ROOT = os.environ.get("MAP_DATA_DIR", "/output")

# Home route (optional)
#@app.route("/")
#def home():
#    return "Hello, World!"

@app.route("/__routes")
def routes():
    return "<br>".join(r.rule for r in app.url_map.iter_rules())

# Register blueprint
#app.register_blueprint(map_blueprint, url_prefix="/map")
app.register_blueprint(map_blueprint)

# Run locally
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
