import xml.etree.ElementTree as et
import dateutil.parser as parser
import pandas as pd
import datetime
from avia_app.query_parser.timezone import get_time_by_local

steps_dict = {'OnwardPricedItinerary': 'start',
              'ReturnPricedItinerary': 'finish', 'Pricing': 'price'}

CONFIG_FLIGHT = \
    {
        'Carrier': {
            'dtype': 'text',
            'attr': {
                'id': {
                    'dtype': 'text',
                    'attr': False,
                    'descrip': 'Airline_id'
                }
            },
            'descrip': 'Airline'
        },
        'FlightNumber': {
            'dtype': 'int',
            'attr': False,
            'descrip': 'Number_of_flight'
        },
        'Source': {
            'dtype': 'text',
            'attr': False,
            'descrip': 'From'
        },
        'Destination': {
            'dtype': 'text',
            'attr': False,
            'descrip': 'To'
        },
        'DepartureTimeStamp': {
            'dtype': 'datetime',
            'attr': False,
            'descrip': 'Time_from'
        },
        'ArrivalTimeStamp': {
            'dtype': 'datetime',
            'attr': False,
            'descrip': 'Time_to'
        },
        'Class': {
            'dtype': 'text',
            'attr': False,
            'descrip': 'Class'
        },
        'NumberOfStops': {
            'dtype': 'int',
            'attr': False,
            'descrip': 'Count_stops'
        },
        'FareBasis': {
            'dtype': 'id',
            'attr': False,
            'descrip': 'Trip_id'
        },
        'WarningText': {
            'dtype': 'text',
            'attr': False,
            'descrip': 'Description'
        },
        'TicketType': {
            'dtype': 'text',
            'attr': False,
            'descrip': 'Type_ticket'
        }

    }
CONFIG_PRICE = \
    {
        'ServiceCharges': {
            'dtype': 'float',
            'attr': {
                'type': {
                    'dtype': 'text',
                    'attr': False,
                    'descrip': 'Person_type'
                },
                'ChargeType': {
                    'dtype': 'text',
                    'attr': False,
                    'descrip': 'Rate_type'
                }
            },
            'descrip': 'Charges'
        },
    }


def parse_step(node, timezone):
    tag = node.tag
    l_step = list()
    if tag in steps_dict:
        l_step = parse_flights(node, tag, timezone)
    return l_step


def get_tag(root, config, attr=None):
    tags = dict()
    for tag in config:
        if attr:
            item = root.attrib
            if len(item) > 1:
                item = {k: item[k] for k in item if k == tag}
        else:
            item = root.find(tag) if root is not None else None
        if config[tag]['attr']:
            tags.update(get_tag(item, config[tag]['attr'], attr=True))
        data = check_dtype(item, config, attr)
        tags.update(data)
    return tags


def check_dtype(item, config, attr):
    d = dict()
    if attr is not None:
        tag = next(iter(item))
        data = item[tag]
    else:
        tag = item.tag
        data = item.text
    if tag in config:
        descrip = config[tag]['descrip']
        dtype = config[tag]['dtype']
        if dtype == 'datetime':
            data = parser.parse(data)
        elif dtype == 'int':
            data = int(data)
        elif dtype == 'float':
            data = float(data)
        elif dtype == 'id':
            data = hash(data.strip())
    d[descrip] = data
    return d


def parse_flights(node, tag, timezone):
    trip_flights = list()
    transfer_flight = None
    for cur_flight in range(len(node.findall('.//Flight')) - 1, -1, -1):
        row = get_tag(node.findall('.//Flight')[cur_flight], CONFIG_FLIGHT)
        row['Tag'] = tag
        from_local_t = get_time_by_local(row['From'], row['Time_from'],timezone)
        to_local_t = get_time_by_local(row['To'], row['Time_to'],timezone)
        if from_local_t['code'] == 200 and to_local_t['code'] == 200:
            row['Time_from_local'] = parser.parse(from_local_t['data'])
            row['Time_to_local'] = parser.parse(to_local_t['data'])
        if cur_flight > 0:
            row['transfer_to'] = transfer_flight
            transfer_flight = row['Number_of_flight']
        else:
            row['transfer_to'] = transfer_flight
        trip_flights.append(row)
    return trip_flights


def parse_trip_price(trip, trip_id):
    trip_prices = list()
    for price in trip.findall('.//Pricing'):
        for single_price in price.findall('ServiceCharges'):
            price_d = dict()
            price_d.update(check_dtype(single_price, CONFIG_PRICE, attr=None))
            price_d['currency'] = price.attrib['currency']
            price_d['Trip_id'] = trip_id
            price_attrib = single_price.attrib
            if price_attrib:
                for k in price_attrib:
                    item = {k: price_attrib[k]}
                    price_d.update(
                        check_dtype(item,
                                    CONFIG_PRICE[single_price.tag]['attr'],
                                    attr=True))
            trip_prices.append(price_d)
    return trip_prices


# -========================================================================
def get_xml_root(xml):
    folder = f'xmls/{xml}.xml'
    tree = et.parse(folder)
    root = tree.getroot()
    return root


def get_trips(root):
    if 'Flights' == root.tag:
        return [root]
    flights = list()
    for child in root:
        flights += get_trips(child)
    return flights


def parse_xml(timezone, xml):
    root = get_xml_root(xml)
    trips = get_trips(root)
    flights = list()
    prices = list()
    for trip in trips:
        flight = list()
        for trips_step in list(trip):
            trips_step = parse_step(trips_step, timezone)
            if trips_step:
                flight.extend(trips_step)
        if flight:
            flights.extend(flight)
            trip_id = flight[0]['Trip_id']
        price = parse_trip_price(trip, trip_id)
        if price:
            prices.extend(price)
    return flights, prices


def get_df_by_data(data):
    return pd.DataFrame(data=data)
