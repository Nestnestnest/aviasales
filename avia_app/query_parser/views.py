from flask import Blueprint, render_template, request, jsonify, Response, \
    redirect, url_for
from .parser_input import get_global_info
from .get_flights import show_flights

query_parser_app = Blueprint('query_parser_app', __name__)


@query_parser_app.route('/', methods=['GET'])
def get_index():
    return render_template('index.html')

import datetime
@query_parser_app.route('/get_flight', methods=['POST'])
def get_flight():
    print(request.form)
    t1 = datetime.datetime.now()
    global_info, xml = get_global_info(request.form)
    a = show_flights(global_info,xml)
    print(datetime.datetime.now()-t1)
    # return (jsonify(show_flights())

    return jsonify(a=200)
