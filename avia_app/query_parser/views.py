from flask import Blueprint, render_template, request, jsonify
from .parser_input import get_global_info
from .get_flights import show_flights

query_parser_app = Blueprint('query_parser_app', __name__)


@query_parser_app.route('/', methods=['GET'])
def get_index():
    return render_template('index.html')


@query_parser_app.route('/get_flight', methods=['POST'])
def get_flight():
    global_info, xml = get_global_info(request.form)
    return jsonify(show_flights(global_info, xml))
