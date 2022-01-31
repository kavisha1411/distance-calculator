from pathlib import Path
from distance import Distances
import requests
import csv

BASE_DIR = Path(__file__).resolve().parent.parent
distObj = None


class TestDistances(object):
    API_KEY = '3442b681ec7d6f78b7b9789679841c27'
    api_url = 'http://api.positionstack.com/v1/forward?'

    def setup(self):
        global distObj
        distObj = Distances()

    def test_without_api(self):
        api_url = self.api_url + 'access_key=ABC&query=XYZ'
        response = requests.get(api_url)
        assert response.status_code == 401

    def test_without_query(self):
        api_url = self.api_url + f'access_key={self.API_KEY}&query='
        response = requests.get(api_url)
        assert response.status_code == 422

    def test_correct_query(self):
        example_address = "Sint Janssingel 92, 5211 DA 's-Hertogenbosch, The Netherlands"
        api_url = self.api_url + f'access_key={self.API_KEY}&query={example_address}'
        response = requests.get(api_url)
        assert response.status_code == 200

    def test_function_without_apikey(self):
        assert distObj.sort_and_display('', {}, self.api_url) == []

    def test_function_without_query(self):
        assert distObj.sort_and_display(self.API_KEY, {}, self.api_url) == []

    def test_without_headquarters(self):
        address_dict = {
            'Eastern Enterprise B.V.': 'Deldenerstraat 70, 7551AH Hengelo, The Netherlands',
            'Eastern Enterprise ': '46/1 Office no 1 Ground Floor , Dada House , Inside dada silk mills compound, Udhana Main Rd, near Chhaydo Hospital, Surat, 394210, India',
        }
        assert distObj.sort_and_display(self.API_KEY, address_dict, self.api_url) == []

    def test_correct_response(self):
        address_dict = {
            'Adchieve HQ': "Sint Janssingel 92, 5211 DA 's-Hertogenbosch, The Netherlands",
            'Eastern Enterprise B.V.': 'Deldenerstraat 70, 7551AH Hengelo, The Netherlands',
        }
        response = distObj.sort_and_display(self.API_KEY, address_dict, self.api_url)
        assert response[0]['name'] == 'Eastern Enterprise B.V.'

        test_file = str(BASE_DIR) + '/tests/test_distances.csv'
        with open(test_file, "w") as csvfile:
            fieldnames = ['Sr.no', 'distance', 'name', 'address']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            count = 1
            for address in response:
                writer.writerow({'Sr.no': count, 'distance': address['distance'],
                                 'name': address['name'], 'address': address['address']})
                count += 1

        with open(test_file, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                assert row['name'] == 'Eastern Enterprise B.V.'
