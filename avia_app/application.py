from flask import Flask
from flask_redis import FlaskRedis
import atexit

redis_client = FlaskRedis(host='redis')


def create_app(config_filename):
    app = Flask(__name__)
    app.config['REDIS_URL'] = 'redis://redis/0'
    redis_client.init_app(app)
    app.config.from_object(config_filename)
    from query_parser.views import query_parser_app
    app.register_blueprint(query_parser_app)

    return app


def stop_program():
    print("Program was stopped\n")


atexit.register(stop_program)
