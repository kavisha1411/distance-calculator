import requests
import csv
from math import cos, sin, sqrt, radians, asin
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


class Distances:
    def haversine_calculation(self, lat1, lon1, lat2, lon2):
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        difference_lon = lon2 - lon1
        difference_lat = lat2 - lat1
        haversine = sin(difference_lat/2)**2 + cos(lat1) * cos(lat2) * sin(
            difference_lon/2)**2

        d = 2 * 6371 * asin(sqrt(haversine))
        return d

    def calculate_distance(self, API_KEY, address_dict, endpoint):
        add_list = []
        hq = {}

        for name, address in address_dict.items():
            api_url = endpoint + f'access_key={API_KEY}&query={address}'
            response = requests.get(api_url)

            if name == 'Adchieve HQ':
                if response.json()['data'][0]:
                    latitude = response.json()['data'][0].get('latitude')
                    longitude = response.json()['data'][0].get('longitude')
                    hq['latitude'] = latitude
                    hq['longitude'] = longitude
                    hq['name'] = name
                    hq['address'] = address
            else:
                if response.json()['data'][0]:
                    latitude = response.json()['data'][0].get('latitude')
                    longitude = response.json()['data'][0].get('longitude')
                    add_list.append({'latitude': latitude,
                                     'longitude': longitude,
                                     'name': name,
                                     'address': address})

        if hq:
            for address in add_list:
                distance = self.haversine_calculation(
                    hq['latitude'], hq['longitude'],
                    address['latitude'], address['longitude'])
                distance = "{:.2f} km".format(distance)
                address['distance'] = distance
            return sorted(add_list, key=lambda x: x['distance'])
        else:
            return []

    def sort_and_display(self, API_KEY, address_dict, endpoint):
        count = 1
        sorted_dict = self.calculate_distance(API_KEY, address_dict, endpoint)
        for address in sorted_dict:
            print('{}, {}, {}, {}'.format(
                count, address['distance'], address['name'],
                address['address']))
            count += 1
        print(sorted_dict)
        return sorted_dict

    def write_to_csv(self, sorted_dict):
        filepath = str(BASE_DIR) + '/distances/distances.csv'
        with open(filepath, "w") as csvfile:
            fieldnames = ['Sr.no', 'distance', 'name', 'address']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            count = 1
            for address in sorted_dict:
                writer.writerow({'Sr.no': count,
                                 'distance': address['distance'],
                                 'name': address['name'],
                                 'address': address['address']})
                count += 1
        csvfile.close()


API_KEY = '3442b681ec7d6f78b7b9789679841c27'
endpoint = 'http://api.positionstack.com/v1/forward?'
address_dict = {
    'Adchieve HQ': "Sint Janssingel 92, 5211 DA 's-Hertogenbosch, The Netherlands",
    'Eastern Enterprise B.V.': 'Deldenerstraat 70, 7551AH Hengelo, The Netherlands',
    'Eastern Enterprise ': '46/1 Office no 1 Ground Floor , Dada House , \
        Inside dada silk mills compound, Udhana Main Rd, near Chhaydo Hospital, Surat, 394210, India',
    'Adchieve Rotterdam': 'Weena 505, 3013 AL Rotterdam, The Netherlands',
    'Sherlock Holmes': '221B Baker St., London, United Kingdom',
    'The White House': '1600 Pennsylvania Avenue, Washington, D.C., USA',
    'The Empire State Building': '350 Fifth Avenue, New York City, NY 10118',
    'The Pope': 'Saint Martha House, 00120 Citta del Vaticano, Vatican City',
    'Neverland': '5225 Figueroa Mountain Road, Los Olivos, Calif. 93441, USA',
}

dist = Distances()
sorted_dict = dist.sort_and_display(API_KEY, address_dict, endpoint)
dist.write_to_csv(sorted_dict)
