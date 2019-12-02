import io
import requests
import pandas as pd
import redis
import pytz
from tzlocal import get_localzone
from datetime import datetime
import json

r = redis.Redis('localhost')


def search_timezone_by_iata(search_code):
    status = check_iata_spr()
    if status == 200:
        search_code = search_code.upper()
        timezone = r.hget('iata_timezone', search_code)
        if timezone is not None:
            return {'code': 200, 'data': timezone.decode('UTF-8')}
        return {'code': 500, 'msg': 'No data by key in redis'}
    return status


def get_iata_country_spr():
    url = "https://raw.githubusercontent.com/opentraveldata/opentraveldata/master/opentraveldata/optd_por_public.csv"
    try:
        s = requests.get(url).content
    except ConnectionError:
        return {'code': 500, 'msg': 'ConnectionError'}
    country_map = pd.read_csv(io.StringIO(s.decode('utf-8')), sep='^')
    iata_dict = country_map.loc[:,
                ['iata_code', 'country_code', 'timezone']].drop_duplicates(
        subset=['iata_code']).to_dict(orient='records')
    iata_timezone = {k['iata_code']: k['timezone'] for k in iata_dict}
    timezone_country = {k['iata_code']: k['timezone'] for k in iata_dict}
    r.hmset('iata_timezone', iata_timezone)
    check_r = r.exists('iata_timezone')
    if check_r:
        return {'code': 200}
    else:
        return {'code': 500, 'msg': 'No data in redis'}


def check_iata_spr():
    if not r.exists('iata_timezone'):
        load_spr = get_iata_country_spr()
        if 'code' in load_spr:
            if load_spr['code'] == 200:
                return 200
        return load_spr
    else:
        return 200


def get_time_by_local(iata_code, dt):
    timezone = search_timezone_by_iata(iata_code)
    if timezone['code'] == 200:
        timezone = pytz.timezone(timezone['data'])
        timezone_dt = timezone.localize(dt)
        local_zone = pytz.timezone(str(get_localzone()))
        local_dt = timezone_dt.astimezone(local_zone)
        local_dt = datetime.strftime(local_dt, '%Y-%m-%d %T')
        return {'code': 200, 'data': local_dt}
    return timezone


# t1 = datetime.now()
print(get_time_by_local('svo', datetime(2002, 10, 27, 6, 0, 0)))
# print(datetime.now() - t1)
