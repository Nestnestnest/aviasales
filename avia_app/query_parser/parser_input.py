from flask import request
from datetime import datetime
from .converters import get_local_cur_by_timezone


def get_global_info(request_form):
    global_struct = dict()
    local_zone, from_airport, to_airport, when, when_return, who, xml = get_post_params(
        request_form,
        'local_zone', 'FROM', 'TO', 'WHEN', 'WHEN_return', 'WHO', 'xml')
    global_struct['timezone'] = 'Europe/Moscow'
    if local_zone != 'null' and local_zone is not None:
        global_struct['timezone'] = local_zone
        local_curr = get_local_cur_by_timezone(local_zone)
        global_struct['Currency'] = local_curr

    passangers = parse_who_fly(who)
    global_struct['passangers'] = passangers
    trip_points = parse_from_to(from_airport, to_airport)
    global_struct['trip_points'] = trip_points
    arrival_dates = parse_arrival_dates(Start_date=when,
                                        Finish_date=when_return)
    global_struct['dates'] = arrival_dates
    return global_struct, xml


def get_post_params(request_form, *args):
    vars = list()
    for arg in args:
        if arg in request_form:
            vars.append(request_form[arg])
        else:
            vars.append(None)
    return tuple(vars)


def parse_who_fly(who: str):
    pass_type = ['SingleAdult', 'SingleChild', 'SingleInfant']
    who = who.split('-')
    passengers = dict()
    for i, p_count in enumerate(who):
        if int(p_count):
            passengers[pass_type[i]] = int(p_count)
    return passengers


def parse_from_to(*args):
    return [arg for arg in args]


def parse_arrival_dates(**dates):
    return {date: datetime.strptime(dates[date], '%Y-%m-%d') for date in
            dates
            if dates[date]}
