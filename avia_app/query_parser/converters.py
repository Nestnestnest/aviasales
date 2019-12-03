import ccy
from currency_converter import CurrencyConverter

c = CurrencyConverter()


def get_country_by_timezone(timezone):
    return r.hget('timezone_country', timezone).decode('UTF-8')


def get_currency_by_country(country):
    return ccy.countryccy(country.upper())


def convert_currency(money, from_cur, to_cur):
    return c.convert(money, from_cur, to_cur)


def get_local_cur_by_timezone(timezone):
    country = get_country_by_timezone(timezone)
    if country:
        local_currency = get_currency_by_country(country)
        return local_currency
    else:
        return None


if __name__ == '__main__':
    print(get_local_cur_by_timezone('Europe/Moscow'))
