import requests
import logging
import urllib
import json
from bs4 import BeautifulSoup
from exceptions import *

logging.basicConfig(
            level=logging.DEBUG,  # Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Log message format
        )


class ConadScraper:
    def __init__(self):
        self.cookie = None

    @property
    def headers(self):
        return {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:131.0) Gecko/20100101 Firefox/131.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Referer": "https://spesaonline.conad.it/home",
            "Connection": "keep-alive",
            "Cookie": self.cookie if self.cookie else "ecAccess=eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJlY0FjY2VzcyIsInRpbWVzdGFtcCI6MTcyODQ5NjI4MTEyMCwidHlwZU9mU2VydmljZSI6Ik9SREVSX0FORF9DT0xMRUNUIiwicG9pbnRPZlNlcnZpY2VJZCI6IjAwNjI4MCIsImNhcnRJZCI6ImMtcy1DLTI0LTA4NDM4OTgwIiwiYW5vbnltb3VzQ2FydElkIjoiYzYzY2Q1ZjMtMGJkYy00MTk2LTg4M2EtMmUzY2U1NmVlNzlkIiwiY2FydENyZWF0aW9uVGltZSI6MTcyODQ5NjI4MzAyMywidGltZXNsb3RFeHBpcmF0aW9uIjowLCJuU3RvcmVzRm91bmQiOjE1LCJtaXNzaW5nQ2FydENvdW50ZXIiOjAsImNsQ291bnRyeSI6IlRSIiwiaXNzIjoiY29uYWQiLCJpYXQiOjE3Mjg1ODk3Mjd9.FzMcW1JQNOf_75RKOcBTCGSOI63I4kOLN45WGbBbbjA; Path=/; Domain=.conad.it; Expires=Sat, 11-Oct-2025 01:37:59 GMT; Max-Age=31556952; Secure; HttpOnly; SameSite=None",            # Truncated for brevity
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Priority": "u=0, i",
            "TE": "trailers"
        }

    @staticmethod
    def get_parent_category_id(soup):
        return soup.find('a')['data-target']

    @staticmethod
    def product_info(soup):
        """
        Get product info
        :param soup:
        :return:
        """
        product_cards = soup.find_all("div", class_="component-ProductCard")
        return [json.loads(product['data-product']) for product in product_cards if product.get('data-product')]

    @staticmethod
    def generate_scrape_urls(hrefs, url):
        return [url+ href for href in hrefs]

    @staticmethod
    def get_total_pages(soup):
        total_pages = len(soup.find("ul", class_='uk-pagination').find_all('li')) - 1
        return total_pages

    @staticmethod
    def product_info(soup):
        """
        Get product info
        :param soup:
        :return:
        """
        product_cards = soup.find_all("div", class_="component-ProductCard")
        return [json.loads(product['data-product']) for product in product_cards if product.get('data-product')]

    @staticmethod
    def get_sub_category_list(soup, parent_category_id):
        subcatList = soup.find('ul', class_='subcatList', attrs={'data-target': str(parent_category_id)})
        return subcatList

    def get_sub_categories_hrefs(self, parent_category_id, soup):
        """
        Each Parent category composed by subcategories, this method, collects all subcategories and their href links to scrape
        :param parent_category_id:
        :param soup:
        :return:
        """
        logging.info("Sub categories hrefs collecting")
        subcatList = self.get_sub_category_list(soup, parent_category_id)
        subcatLists = subcatList.find_all('li', class_=lambda x:x !='all')
        sub_category_hrefs = [s_category.find('a').get('href') for s_category in subcatLists]
        logging.info("Sub categories urls collected")
        return sub_category_hrefs

    @staticmethod
    def get_menu_items(soup):
        """
        Get menu items and select All Product Item
        :return:
        """

        # TODO: Retry will be added
        menu_items = soup.find_all('li', class_='sub-menu voce-main-menu')[0]
        return menu_items

    @staticmethod
    def get_parent_categories( menu_items):
        """
        Method gets parent categories list
        :return:
        """
        parent_categories = menu_items.find_all('li', class_='cat')
        return parent_categories


    def _request(self, url, method, headers=None, body=None):
        try:
            logging.info(f"Request sent: {url} | method: {method}")
            response = requests.request(method=method, url=url, headers=headers, json=body)
            return response if response.status_code == 200 else None
        except Exception as e:
            raise e

    def html_parser(self, url):
        """
        Html Parser
        :param url:
        :return:
        """
        logging.info("HTML Parsing starting for {}".format(url))
        html_doc = self._request(url=url, method="GET", headers=self.headers)
        try:
            soup = BeautifulSoup(html_doc.text, 'html.parser')
            return soup
        except AttributeError as e:
            raise e

    def get_closest_market(self, address):
        """
        Get closest market from list of markets by sending a coordinates

        :param address_coordinations:
        :return:
        """
        logging.info("Getting market info")
        body = {"latitudine":address["coordinations"]["lat"],
                "longitudine":address["coordinations"]["lng"],
                "typeOfService":None,
                "partial":False}
        closest_market_info = self._request(url=CLOSEST_STORE_URL, method="POST", body=body)
        if closest_market_info:
            try:
                market = closest_market_info.json()
                return market["data"]["orderAndCollect"]["pointOfServices"][0], len(market["data"]["orderAndCollect"]["pointOfServices"])
            except KeyError as ke:
                raise ke("Could not get the closest market")

    def scrape_market(self):
        """
        It's main function to scrape specific market by using the cookie.
        :return:
        """
        soup = self.html_parser(SHOPPING_ONLINE_HOME)
        menu_items = self.get_menu_items(soup=soup)
        logging.info("Menu Items retrieved")
        parent_categories = self.get_parent_categories(menu_items=menu_items)
        logging.info("Parent Categories retrieved")

        for parent_category in parent_categories:
            logging.info("Parent Category : {}".format(parent_category.text.strip()))
            parent_category_id = self.get_parent_category_id(parent_category)
            sub_categories_hrefs = self.get_sub_categories_hrefs(parent_category_id=parent_category_id, soup=soup)
            scrape_urls = self.generate_scrape_urls(hrefs=sub_categories_hrefs, url=SHOPPING_ONLINE)
            self.scrape_sub_categories(scrape_urls)

    def scrape_sub_categories(self, scrape_urls):
        """
        Scrape method for sub categories. Scraping starts by taking the scrape_urls. Since there is a pagination

        :param scrape_urls:
        :return:
        """
        for scrape_url in scrape_urls:
            logging.info("Scraping {}".format(scrape_url))
            soup = self.html_parser(url=scrape_url)
            initial_page_number = 1
            total_pages = self.get_total_pages(soup=soup)
            products = self.scrape_product(scrape_url=scrape_url, initial_page_number=initial_page_number, total_pages=total_pages)
            print(products)

    def scrape_product(self, scrape_url, initial_page_number, total_pages):
        """
        Scrape products page to page
        :param initial_page_number:
        :param total_pages:
        :return:
        """
        products = []
        while initial_page_number <= total_pages:
            page_number = initial_page_number
            url = scrape_url + "?page={}".format(page_number)
            logging.info("Scraping {}".format(url))
            soup = self.html_parser(url=url)
            product = self.product_info(soup)
            products.extend(product)
            initial_page_number += 1
        return products

    def set_cookie(self, market, address, total_markets_number):
        """
        Conad web site that send you set-cookie which is inside the response header, we can scrape the website by using it.

        :param address_coordinations:
        :param market:
        :return:
        """
        logging.info("In order to scrape the product, cookie is set by sending requests")
        body = {"pointOfServiceId": market["name"],
                "becommerce": "sap",
                "typeOfService": "ORDER_AND_COLLECT",
                "deliveryAddress": market["address"]["formattedAddress"],
                "completeAddress": {
                    "line1": market["address"]["formattedAddress"],
                    "formattedAddress": market["address"]["formattedAddress"],
                    "town": market["address"]["town"],
                    "line2": market["address"]["line2"],
                    "postalCode": market["address"]["postalCode"],
                    "district": "MI",
                    "country":
                        {"isocode": "IT",
                         "name": "Italy"},
                    "latitude": market["geoPoint"]["latitude"],
                    "longitude": market["geoPoint"]["longitude"],
                    "notCompleted": False},
                "latitudine": address["coordinations"]["lat"],
                "longitudine": address["coordinations"]["lng"],
                "nStoresFound": total_markets_number}

        #         body = {
        # 	"pointOfServiceId": "006280",
        # 	"becommerce": "sap",
        # 	"typeOfService": "ORDER_AND_COLLECT",
        # 	"deliveryAddress": "Piazzale Bologna, 7, 20139 Milano MI, Italy",
        # 	"completeAddress": {
        # 		"line1": "Piazzale Bologna, 20139, Milano, Italy",
        # 		"formattedAddress": "Piazzale Bologna, 7, 20139 Milano MI, Italy",
        # 		"town": "Milano",
        # 		"line2": "7",
        # 		"postalCode": "20139",
        # 		"district": "MI",
        # 		"country": {
        # 			"isocode": "IT",
        # 			"name": "Italy"
        # 		},
        # 		"latitude": 45.44396,
        # 		"longitude": 9.2237207,
        # 		"notCompleted": False
        # 	},
        # 	"latitudine": 45.444012,
        # 	"longitudine": 9.222511,
        # 	"nStoresFound": "15"
        # }

        resp = self._request(EACCESS_URL, method="POST", body=body, headers=self.headers)
        if not resp:
            logging.info("Set cookie could not completed")
            return
        self.cookie = resp.headers['set-cookie']
        logging.info("Set cookie method completed")

    def convert_address_to_long_lat(self, address):
        """
        Converts the address to a long lat dynamically.

        :param address:
        :return:
        """

        url = GOOGLE_GEO_SERVICE.format(address, GOOGLE_API_KEY)
        response = self._request(url=url, method="GET")
        if response:
            address = response.json()
            result = address["results"]
            coordinations = result[0]["geometry"]["location"]
            try:
                return {
                        "coordinations": coordinations
                        }
            except KeyError as ke:
                raise ke("Could not get the location of address")

    def run(self, address):
        logging.info("Scraping starting for {}".format(address))
        address = self.convert_address_to_long_lat(address)
        if not address:
            logging.warning(f"Failed to convert address to coordinates: {address}")
            return

        market, total_markets_number = self.get_closest_market(address=address)

        if not market:
            logging.info("Could not get the market")
            return

        self.set_cookie(market, address, total_markets_number)
        logging.info("Scraping for market starting {}".format(market["address"]["formattedAddress"]))
        self.scrape_market()


if __name__ == '__main__':
    from parser import EnvArgumentParser

    parser = EnvArgumentParser(description='CONAD SCRAPER')
    SHOPPING_ONLINE_ENTRY_URL = "https://spesaonline.conad.it/entry"
    SHOPPING_ONLINE_HOME = 'https://spesaonline.conad.it/home'
    SHOPPING_ONLINE = 'https://spesaonline.conad.it'
    EACCESS_URL = "https://spesaonline.conad.it/api/ecommerce/it-it.set-ecaccess.json"

    ADDRESS1 = "Viale Lucania 22, Milan"
    CLOSEST_STORE_URL = "https://spesaonline.conad.it/api/ecommerce/it-it.stores.json"
    GOOGLE_API_KEY = "AIzaSyDpQt6u2xUdzYG852YJ9f_JAvcgvHk5zPA"
    GOOGLE_GEO_SERVICE = "https://maps.googleapis.com/maps/api/geocode/json?address={}&key={}"

    # CONNECTIONS
    parser.add_argument('--shopping-online-entry-url', metavar='SHOPPING_ONLINE_ENTRY_URL',
                        help='SHOPPING_ONLINE_ENTRY_URL',
                        required=True)
    parser.add_argument('--template-path', metavar='TEMPLATE_PATH',
                        help='TEMPLATE PATH',
                        required=True)
    parser.add_argument('--mail-username', metavar='MAIL_USERNAME',
                        help='MAIL USERNAME',
                        required=True)
    parser.add_argument('--mail-password', metavar='MAIL_PASSWORD',
                        help='MAIL PASSWORD',
                        required=True)
    parser.add_argument('--mail-sender', metavar='MAIL_SENDER',
                        help='MAIL SENDER',
                        required=True)
    conad_scraper = ConadScraper()
    conad_scraper.run(ADDRESS1)

