from .parseXML import parse_xml, get_df_by_data
from .converters import convert_currency
from .timezone import parse_ts_to_datetime, parse_datetime_to_ts


def show_flights(global_info, xml):
    '''
    Parse xml and return json with aggregates flights and trips and fill
    max/min/optimal time/price
    :param global_info: dict of input params
    :param xml: xml_name
    :return: parsed xml
    :rtype: dict
    '''
    flights, prices = parse_xml(global_info, xml)
    flights = get_df_by_data(flights)
    flights = flights.sort_values(
        ['Trip_id', 'Tag', 'transfer_to', 'Time_from_local']).reset_index(
        drop=True)
    flights = del_error_trips(global_info['trip_points'], flights)
    agg_prices = get_agg_prices(global_info, prices)
    global_info = convert_trips_to_json(global_info, flights, agg_prices)
    global_info['flights'] = fill_max_min(global_info['flights'],
                                          {'price': 'total_price',
                                           'time': 'total_time'})
    fill_optimal_flights(global_info['flights'])
    return {'data': global_info}


def convert_trips_to_json(global_info, flights, agg_prices):
    '''
    Translate flights_df to nested dict and merge prices
    to all flight's (by local currency)
    :param global_info:  dict of input params
    :param flights:  df of flight's
    :param agg_prices: df of aggregate price by flight's
    :return: nested dict flight's with price
    '''
    there = 'OnwardPricedItinerary'
    times = ['OnwardPricedItinerary_time', 'ReturnPricedItinerary_time']
    times = times[:len(global_info['dates'])]
    res = dict()
    prev_id = None
    total_duration = dict()
    for index, row in flights.iterrows():
        id_trip = row['Trip_id']
        if id_trip not in res:
            if prev_id is not None:
                for t in times:
                    total_time += res[prev_id][t]
                res[prev_id]['total_time'] = total_time
            prev_id = id_trip
            total_time = 0
            res[id_trip] = {'there': [], 'back': [], 'notes': []}
            price = get_agg_price_by_id(id_trip, agg_prices)
            res[id_trip]['total_price'] = price
        if row['Tag'] == there:
            var = res[id_trip]['there']
        else:
            var = res[id_trip]['back']
        flight = get_flight(row, var)
        if var:
            res[id_trip][f"{row['Tag']}_time"] += flight['duration'] + var[-1][
                'transfer_time']
            total_duration[id_trip] = res[id_trip][f"{row['Tag']}_time"]
        else:
            res[id_trip][f"{row['Tag']}_time"] = flight['duration']
            total_duration[id_trip] = res[id_trip][f"{row['Tag']}_time"]

        var.append(flight)
    global_info['flights'] = res
    return global_info


def fill_max_min(d, chooses, max_key='max', min_key='min'):
    for choose in chooses:
        orig_k = chooses[choose]
        id_time_d = {k: d[k][orig_k] for k in d if
                     orig_k in d[k]}
        if id_time_d:
            max_val = max(id_time_d.items(), key=lambda x: x[1])
            min_val = min(id_time_d.items(), key=lambda x: x[1])
        for k, v in id_time_d.items():
            if v == max_val[1]:
                d[k]['notes'].append(f'{max_key}_{choose}')
            elif v == min_val[1]:
                d[k]['notes'].append(f'{min_key}_{choose}')
            if v <= (min_val[1] + 0.40 * min_val[1]):
                d[k]['notes'].append(f'optimal_{choose}')

    return d


def fill_max_min_price(agg_df, agg_col):
    agg_df.loc[agg_df[agg_col] == agg_df[
        agg_col].min(), 'price_status'] = 'min price'
    agg_df.loc[agg_df[agg_col] == agg_df[
        agg_col].max(), 'price_status'] = 'max price'


def get_agg_price_by_id(id, agg_df):
    s = agg_df.loc[agg_df['Trip_id'] == id, 'Charges']
    price = float(format(s.iloc[0], '.2f'))
    return price


def solve_duration(duration):
    hours = duration.seconds // 3600
    minutes = (duration.seconds // 60) % 60
    res = f""
    if hours == 0:
        pass
    elif hours == 1:
        res = "1 час"
    elif 1 < hours < 5:
        res = f"{hours} часа"
    else:
        res = f"{hours} часов"
    res += f" {minutes} минут"
    return res


def get_duration_flight(row):
    duration = row['Time_to_local'] - row['Time_from_local']
    return duration


def transfer_time(transfer_start, transfer_end):
    duration = transfer_end - transfer_start
    # res = solve_duration(duration)
    return duration


def get_flight(row, transfer):
    if transfer:
        transfer = transfer[-1]
        transfer_end = row['Time_from_local']
        transfer_start = transfer['time_stop_ts']
        transfer['transfer'] = row['Number_of_flight']
        transfer['transfer_time'] = transfer_time(transfer_start, transfer_end)

    duration = get_duration_flight(row)
    trip = {'carrier': row['Airline'],
            'carrier_tag': row['Airline_id'],
            'class': row['Class'],
            'type_ticket': row['Type_ticket'],
            'flight_number': row['Number_of_flight'],
            'count_stops': row['Count_stops'],
            'from': row['From'],
            'to': row['To'],
            'time_start': row['Time_from'],
            'time_stop': row['Time_to'],
            'time_start_ts': row['Time_from_local'],
            'time_stop_ts': row['Time_to_local'],
            'duration': duration,
            'transfer': '',
            'transfer_time': ''}

    return trip


def get_agg_prices(global_info, prices: dict):
    prices = get_df_by_data(prices)
    if 'Currency' in global_info:
        prices['Charges'] = prices.apply(lambda row: convert_currency(
            row['Charges'], row['currency'], global_info['Currency']), axis=1)
    agg_prices = prices.groupby(['Trip_id']).agg(
        {'Charges': 'sum'}).reset_index()
    return agg_prices


def fill_optimal_flights(flights):
    optimals = ['optimal_price', 'optimal_time']
    for f in flights:
        notes = flights[f]['notes']
        flag_opt = all(o in notes for o in optimals)
        if flag_opt:
            flights[f]['notes'].append('best')


def del_error_trips(trip_points, flights):
    tag_points = {}
    good_trips = set()
    cols = ['Trip_id', 'Tag', 'From', 'To']
    for index, row in flights[cols].iterrows():
        id_trip = row['Trip_id']
        if id_trip not in tag_points:
            tag_points[id_trip] = [row['From'], row['To']]
        else:
            tag_points[id_trip].extend([row['From'], row['To']])
        check = all(trip in tag_points[id_trip] for trip in trip_points)
        if check:
            good_trips.add(id_trip)
    return flights[flights['Trip_id'].isin(good_trips)]
