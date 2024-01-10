"""Initialize Flask app."""
from flask import Flask

def init_app():
    """Construct core Flask application with embedded Dash app."""
    app = Flask(__name__, instance_relative_config=True,
                template_folder='templates')

    app.config.from_object('config.Config')

    with app.app_context():
        from . import routes

        # Import Dash application
        from .plotlydash.dashboard import init_dashboard
        app = init_dashboard(app)

        return app
