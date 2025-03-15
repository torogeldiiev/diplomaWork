from flask import Flask
from flask_restx import Api, Resource
from .routes.home import home_bp


def create_app():
    app = Flask(__name__)
    api = Api(app, version="1.0", title="My Flask App API", description="A simple API with Swagger documentation")
    return app
