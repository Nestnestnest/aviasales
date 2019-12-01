import xml.etree.ElementTree as et
import dateutil.parser as parser
import pandas as pd
import datetime


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
            'dtype': 'text',
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
    d[descrip] = data
    return d


def parse_flights(node, tag):
    trip_flights = list()
    for flight in node.findall('.//Flight'):
        row = get_tag(flight, CONFIG_FLIGHT)
        row['Tag'] = tag
        trip_flights.append(row)
    return trip_flights


def parse_trip_price(trip, trip_id):
    trip_prices = list()
    for price in trip.findall('.//Pricing'):
        row = get_tag(price, CONFIG_PRICE)
        row['Trip_id'] = trip_id
        if price.attrib:
            row['currency'] = price.attrib['currency']
        trip_prices.append(row)
    return trip_prices


def get_trips(root):
    if 'Flights' == root.tag:
        return [root]
    flights = list()
    for child in root:
        flights += get_trips(child)
    return flights


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
prices = pd.DataFrame(data=prices)
