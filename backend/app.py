from flask import Flask
from whatsapp_ddexplorer import whatsapp_webhook_blueprint
from ai_service_route import routes_blueprint
from whatsapp_ddexplorer import nearby_routes_blueprint  # Import the nearby_routes_ blueprint

app = Flask(__name__)

# Register blueprints
app.register_blueprint(whatsapp_webhook_blueprint, url_prefix='/webhook')
app.register_blueprint(routes_blueprint, url_prefix='/')
app.register_blueprint(nearby_routes_blueprint, url_prefix='/')

if __name__ == '__main__':
    app.run(debug=True)
