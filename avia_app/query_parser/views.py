from flask import Blueprint, render_template, request, jsonify, Response, \
    redirect, url_for
from .parser_input import get_global_info

query_parser_app = Blueprint('query_parser_app', __name__)


@query_parser_app.route('/', methods=['GET'])
def get_index():
    return render_template('index.html')



@query_parser_app.route('/get_flight', methods=['POST'])
def get_flight():
    print(request.form)
    global_info = get_global_info(request.form)

    # return (jsonify(show_flights())



    return jsonify(a=200)
