import xml.etree.ElementTree as et
import dateutil.parser as parser
import pandas as pd
import datetime
from timezone import get_time_by_local
from currency_converter import CurrencyConverter
import pycountry


# tree = et.parse('xmls/RS_Via-3.xml')
# root = tree.getroot()


class Query:
    def __init__(self, xml):
        self.xml = xml

    def get_xml_root(self):
        tree = et.parse(self.xml)
        root = tree.getroot()
        return root


# class ParseTrips:
#     def __init__(self, root):
#         self.root = root
#     def get_trips(self):


first_q = Query('xmls/RS_ViaOW.xml')
root = first_q.get_xml_root()

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


def parse_step(node):
    tag = node.tag
    l_step = list()
    if tag in steps_dict:
        l_step = parse_flights(node, tag)
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


def parse_flights(node, tag):
    trip_flights = list()
    transfer_flight = None
    for cur_flight in range(len(node.findall('.//Flight')) - 1, -1, -1):
        row = get_tag(node.findall('.//Flight')[cur_flight], CONFIG_FLIGHT)
        row['Tag'] = tag
        from_local_t = get_time_by_local(row['From'], row['Time_from'])
        to_local_t = get_time_by_local(row['To'], row['Time_to'])
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


def get_trips(root):
    if 'Flights' == root.tag:
        return [root]
    flights = list()
    for child in root:
        flights += get_trips(child)
    return flights


t1 = datetime.datetime.now()
trips = get_trips(root)
flights = list()
prices = list()
for trip in trips:
    flight = list()
    for trips_step in list(trip):
        trips_step = parse_step(trips_step)
        if trips_step:
            flight.extend(trips_step)
    if flight:
        flights.extend(flight)
        trip_id = flight[0]['Trip_id']
    price = parse_trip_price(trip, trip_id)
    if price:
        prices.extend(price)
df = pd.DataFrame(data=flights)
df = df.sort_values(
    ['Trip_id', 'Tag', 'transfer_to', 'Time_from_local']).reset_index(drop=True)
prices = pd.DataFrame(data=prices)
agg_prices = prices.groupby(['Trip_id']).agg({'Charges': 'sum'}).reset_index()
airports = ['DXB', 'BKK']
trip_struct = dict()
trips = list()
pauses = list()
for i, flight in df.iterrows():
    if i == 0:
        start_f = flight
    elif start_f['Trip_id'] != flight['Trip_id']:
        if start_f['From'] in airports and df.loc[i - 1, 'To'] in airports:
            trip_struct['id'] = start_f['Trip_id']
            trip_struct['from'] = start_f['From']
            trip_struct['to'] = df.loc[i - 1, 'To']
            trip_struct['time'] = df.loc[i - 1, 'Time_to_local'] - start_f[
                'Time_from_local']
            trip_struct['total_price'] = agg_prices.loc[
                agg_prices['Trip_id'] == trip_struct['id'], 'Charges'].values[
                0].round(3)
            trip_struct['currency'] = prices.loc[
                prices['Trip_id'] == trip_struct['id'], 'currency'].values[0]
            trips.append(trip_struct)
            trip_struct = {}
        start_f = flight
    else:
        pauses.append(flight['Time_from_local'] - start_f['Time_to_local'])
print(datetime.datetime.now() - t1)


# def parse_global_configs():
