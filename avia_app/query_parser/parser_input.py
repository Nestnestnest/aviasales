from flask import request
from datetime import datetime
from .converters import get_local_cur_by_timezone


def get_global_info(request_form):
    local_zone, from_airport, to_airport, when, when_return, who = get_post_params(
        'local_zone', 'FROM', 'TO', 'WHEN', 'WHEN_return', 'WHO')
    if local_zone != 'null':
        local_curr = get_local_cur_by_timezone(local_zone)
    print(local_curr)
    passangers = parse_who_fly(who)
    trip_points = parse_from_to(from_airport, to_airport)
    arrival_dates = parse_arrival_dates(Start_date=when,
                                        Finish_date=when_return)


def get_post_params(*args):
    return tuple(request.form[arg] for arg in args)


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
    return {date: datetime.strptime(dates[date], '%Y-%m-%d') for date in dates
            if dates[date]}
