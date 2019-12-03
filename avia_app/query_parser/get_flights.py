from .parseXML import parse_xml, get_df_by_data
from .converters import convert_currency
import math
import datetime


def show_flights(global_info, xml):
    flights, prices = parse_xml(global_info['timezone'], xml)
    flights = get_df_by_data(flights)
    flights = flights.sort_values(
        ['Trip_id', 'Tag', 'transfer_to', 'Time_from_local']).reset_index(
        drop=True)
    prices = get_df_by_data(prices)
    agg_col = 'Charges'
    if 'Currency' in global_info:
        prices['Charges'] = prices.apply(lambda row: convert_currency(
            row['Charges'], row['currency'], global_info['Currency']), axis=1)
    agg_prices = prices.groupby(['Trip_id']).agg(
        {'Charges': 'sum'}).reset_index()
    fill_max_min_price(agg_prices, agg_col)
    trips_json = convert_trips_to_json(global_info, flights, agg_prices)


def convert_trips_to_json(global_info, flights, agg_prices):
    there = 'OnwardPricedItinerary'
    res = dict()
    tag_points = dict()
    for index, row in flights.iterrows():
        id_trip = row['Trip_id']
        if id_trip not in res:
            if tag_points:
                fake_id = check_by_trip_points(global_info['trip_points'],
                                               tag_points)
                tag_points = {}
                if fake_id is not None:
                    res.pop(fake_id, None)
                    continue
            res[id_trip] = {'there': [], 'back': [], 'notes': []}
            price, price_status = get_agg_price_by_id(id_trip, agg_prices)
            res[id_trip]['total_price'] = price
            if isinstance(str, type(price_status)):
                res[id_trip]['notes'].append(price_status)

        if row['Tag'] == there:
            var = res[id_trip]['there']
        else:
            var = res[id_trip]['back']
        flight = get_fligth(row, var)
        if index == 0:
            diff_dt = flight['duration']
            diff_tag = row['Tag']
            diff_id = id_trip
            res[id_trip][f"{row['Tag']}_time"] = diff_dt
            tag_points[id_trip] = {index: [row['From'], row['To']]}
        elif row['Tag'] == diff_tag and id_trip == diff_id:
            res[id_trip][f"{row['Tag']}_time"] += flight['duration']
            tag_points[id_trip].update({index: [row['From'], row['To']]})
        else:
            if tag_points:
                fake_id = check_by_trip_points(global_info['trip_points'],
                                               tag_points)
                tag_points = {}
                if fake_id is not None:
                    res.pop(fake_id, None)
                    continue
            tag_points[id_trip] = {index: [row['From'], row['To']]}
            diff_dt = flight['duration']
            diff_tag = row['Tag']
            diff_id = id_trip
            res[id_trip][f"{row['Tag']}_time"] = diff_dt

        var.append(flight)
    return res


def fill_max_min_price(agg_df, agg_col):
    agg_df.loc[agg_df[agg_col] == agg_df[
        agg_col].min(), 'price_status'] = 'min price'
    agg_df.loc[agg_df[agg_col] == agg_df[
        agg_col].max(), 'price_status'] = 'max price'


def get_agg_price_by_id(id, agg_df):
    s = agg_df.loc[agg_df['Trip_id'] == id, 'Charges']
    price = float(format(s.iloc[0], '.2f'))
    s = agg_df.loc[agg_df['Trip_id'] == id, 'price_status']
    price_status = s.iloc[0]
    return price, price_status


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
    # format = "%Y-%m-%d %H:%M:%S"
    duration = transfer_end - transfer_start,
    # res = solve_duration(duration)
    return duration


def get_fligth(row, transfer):
    if transfer:
        transfer = transfer[-1]
        transfer_end = row['Time_from_local']
        transfer_start = transfer['time_stop']
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
            'time_start': row['Time_from_local'],
            'time_stop': row['Time_to_local'],
            'duration': duration,
            'transfer': '',
            'transfer_time': ''}

    return trip


def check_by_trip_points(trip_points, points):
    start_k = 0
    finish_k = 0
    for id in points:
        trip_id = id
        d = points[id]
        keys = list(d.keys())
        min_k = min(keys)
        max_k = max(keys)

        for start in d[min_k]:
            if start in trip_points:
                start_k += 1
        for finish in d[max_k]:
            if finish in trip_points:
                finish_k += 1
    if start_k + finish_k < 2:
        return trip_id
