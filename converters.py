import pycountry
import requests
import pandas as pd
import io
country = pycountry.countries.get(alpha_2='AU')
print(country)
url = "https://raw.githubusercontent.com/opentraveldata/opentraveldata/master/opentraveldata/optd_por_public.csv"
s = requests.get(url).content
country_map = pd.read_csv(io.StringIO(s.decode('utf-8')), sep='^')
iata_dict = country_map.loc[:,
            ['iata_code', 'country_code', 'timezone']].drop_duplicates(
    subset=['iata_code']).to_dict(orient='records')
a = 100