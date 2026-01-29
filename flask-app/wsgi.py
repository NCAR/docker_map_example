import os
from flask import Flask
from map_api.routes import map_blueprint

# Explicitly tell Flask where static and templates are
app = Flask(
    __name__,
    static_folder=os.path.join(os.path.dirname(__file__), "static"),
    template_folder=os.path.join(os.path.dirname(__file__), "templates")
)
print(app.url_map)

# Home route (optional)
@app.route("/")
def home():
    return "Hello, World!"

@app.route("/__routes")
def routes():
    return "<br>".join(r.rule for r in app.url_map.iter_rules())

# Register blueprint
#app.register_blueprint(map_blueprint, url_prefix="/map")
app.register_blueprint(map_blueprint)

# Run locally
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)


#from flask import Flask
#from map_api.routes import map_blueprint
#
#def create_app():
#    app = Flask(__name__)
#
#    # Example home route
#    @app.route("/")
#    def hello_world():
#        return "Hello, World!"
#
#    # Register your blueprint
#    app.register_blueprint(map_blueprint, url_prefix="/map")
#
#    return app
#
## Create app instance for WSGI servers
#app = create_app()
#
## Run locally for development
#if __name__ == "__main__":
#    app.run(host="0.0.0.0", port=5000, debug=True)
