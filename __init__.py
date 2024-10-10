# product_url = "https://spesaonline.conad.it"
# initial_page_number = 1
# total_pages = len(soup.find("ul", class_='uk-pagination').find_all('li')) - 1
# for s_category in subcatLists:
#     while total_pages >= initial_page_number:
#         href = s_category.find('a').get('href')
#         s_category_id = href.split('--')[-1] # parse frutta-fresca--0101
#         url = product_url + href + "?page{}".format(initial_page_number)
#         products_soup = self.html_parser(url)
#         products = self.get_products(soup=products_soup)
#         initial_page_number += 1


# def scrape_products(self, scrape_urls):
#     for scrape_url in scrape_urls:
#         soup = self.html_parser(url=scrape_url)
#         product_lists = soup.find_all("div", class_="component-ProductCard")
#         initial_page_number = 1
#         total_pages = len(soup.find("ul", class_='uk-pagination').find_all('li')) - 1
#         self.scrape_product(product_lists, initial_page_number, total_pages)

# products = []
# product_lists = soup.find_all("div", class_="component-ProductCard")
# for product in product_lists:
#     product_info = json.loads(product['data-product'])
#     products.append(product_info)
# return products