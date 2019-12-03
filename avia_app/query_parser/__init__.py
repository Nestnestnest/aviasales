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

# VIA_OW
json_client = {
    'flight':
        {
            'FROM': 'DXB',
            'TO': 'BKK',
            'WHEN': '2018-10-27',
            'DIFF_ONE_DAY': 1,
            'WHO': {
                'SingleAdult': 1,
                'SingleChild': 1,
                'SingleInfant': 1
            }
        },
    'return_flight': {}
}
# Via-3
json_client = \
    {
        'flight':
            {
                'FROM': 'DXB',
                'TO': 'BKK',
                'WHEN': '2018-10-22',
                'WHO': {
                    'SingleAdult': 1,
                    'SingleChild': 0,
                    'SingleInfant': 0
                }
            },
        'return_flight':
            {
                'FROM': 'BKK',
                'TO': 'DXB',
                'WHEN': '2018-10-30',
                'WHO': {
                    'SingleAdult': 1,
                    'SingleChild': 0,
                    'SingleInfant': 0
                }
            }
    }
