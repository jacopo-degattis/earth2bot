import os
import json
import time
import requests
import threading
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from calcs import *

class Earth2(object):
    base_uri = None
    headers = None
    sitekey = None
    cookies = None
    user_infos = None
    tokens = []
    bought = 0
    notbought = 0

    def __init__(self):
        # Variables initialization
        self.base_uri = "https://app.earth2.io/graphql"
        self.headers = {"user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 OPR/73.0.3856.284",}
        self.sitekey = "6Le5LnAaAAAAAEk2YEtdy82eq9mUz_qgwcZ7GRa7"
        self.mapboxtoken = "pk.eyJ1IjoiZXYyIiwiYSI6ImNqeTN6azRrOTE0cmUzYmsyYmlyNnRsdGgifQ.-sbiQ3GonUTodPEsji747Q"
        self.mapboxapi = "https://api.mapbox.com/geocoding/v5/mapbox.places/{}.json?types=country%2Cregion%2Cdistrict%2Cplace%2Clocality&access_token={}"
        self.tokens = []

        # Driver initialization
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=chrome_options)

        # Session initialization
        self.s = requests.Session()
        self._load_cookies()

        # Fetch user infos
        self._fetch_user_infos()
        self._print_user_infos()

        # Load threads to process chunks
        buy_threads = threading.Thread(target=self._load_threads, args=())
        token_threads = threading.Thread(target=self._load_threads_recaptcha, args=())
        
        token_threads.start()
        time.sleep(10)
        print("going")
        buy_threads.start()

    def _load_cookies(self, filename="./data/cookies.json"):
        with open(filename, 'r') as jsonCookies:
            local_cookies = json.load(jsonCookies)
            self.s.cookies.set(**local_cookies)

    def _fetch_details_from_coordinates(self, coordinates):
        # Coordinates must be of type string
        response = requests.get(self.mapboxapi.format(coordinates, self.mapboxtoken)).json()
        return response

    def _fetch_user_infos(self):
        page = self.s.get("https://app.earth2.io/#profile")
        soup = BeautifulSoup(page.content, "html.parser")
        s = soup.findAll('script')
        json_dict = str(s).split("riot.auth0user =")[1].split("static_url")[0].strip().replace("'", '"')
        data = u'{}'.format(json_dict)
        self.user_infos = json.loads(data)

    def _print_user_infos(self):
        print(f"[!] Logged in as")
        print(f"username: {self.user_infos['username']}")
        print(f"balance: {self.user_infos['balance']}")
        print(f"networth: {self.user_infos['networth']}")
        print(f"totalTiles: {self.user_infos['totalTiles']}")
        print(f"spent: {self.user_infos['spent']}")
        print(f"===========")

    def _check_tile(self, line):
        valid = False
        try:
            value = int(line)
            valid = True
        except Exception as e:
            valid = False
        return valid

    def _exec(self, query):
        return self.s.post(
            self.base_uri,
            headers=self.headers,
            data={"query":query}
        ).json()

    def _parse_files(self, files):
        chunks = {}
        for f in files:
            current_file = open(f, 'r')
            curr_name = ""
            for line in current_file:
                if 'name=' in line:
                    chunks_name = line.split("name=")[1].strip()
                    curr_name = chunks_name
                    chunks[curr_name] = []
                elif self._check_tile(line):
                    chunks[curr_name].append(int(line))
        return chunks

    def pay(self, tiles):
        print(self.tokens)
        try:
            recaptcha_token = self.tokens.pop(0)
            # query = 'mutation { buyNewLandfield( captcha: "' + recaptcha_token + '", tiles: ' + str(tiles) + ', center: "7.367535, 45.717207", description: "Pollein", location: "Pollein, Aosta Valley, Italy", promoCodeId: "undefined" ) { landfield { id, thumbnail, description, location, forSale, price, center, tileIndexes, owner { username }, transactionSet { price, timeStr, previousOwner { username, } owner { username, } } } } }'
            query = 'mutation { buyNewLandfield( captcha: "' + recaptcha_token + '", tiles: ' + str(tiles) + ', promoCodeId: "undefined" ) { landfield { id, thumbnail, description, location, forSale, price, center, tileIndexes, owner { username }, transactionSet { price, timeStr, previousOwner { username, } owner { username, } } } } }'
            response = self._exec(query)
            print(response)
            return response
        except Exception as e:
            print("err", e)
            pass

    def try_payement(self, name, tiles):
        status = False
        t = threading.currentThread()
        while getattr(t, "do_run", True):
            response = self.pay(str(tiles))
            if response:
                if "errors" in response.keys():
                    if response['errors'][0]['extensions']['code'] == 30001:
                        t.do_run = False
                        break
                else:
                    # TODO: incrementa contatore acquistati
                    print("Comprato: ", str(tiles))
            else:
                status = True
        print(f"[!] Killing thread {name} for id --> {tiles}\n\n")

    def _get_recaptcha_token(self):
        self.driver.get("http://localhost:5000/")
        time.sleep(.1)
        token = self.driver.find_elements_by_class_name("token-container")[0].text
        print(token)
        print("updating")
        self.tokens.append(token)
        print(len(self.tokens))
        # print(token)

    def _load_threads_recaptcha(self):
        for i in range(60):
            print('starting ', i)
            x1 = threading.Thread(target=self._get_recaptcha_token, args=())
            x1.start()
            x1.join()
        # time.sleep(5)
        # self._load_threads_recaptcha()

    def _load_threads(self):
        chunks = self._parse_files(['./data/tiles'])
        for (name, tile_ids) in chunks.items():
            for _id in tile_ids:
                print("loading ", _id)
                x2 = threading.Thread(target=self.try_payement, args=(name, _id))
                x2.start()

e = Earth2()
