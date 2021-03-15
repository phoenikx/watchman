import json
import pprint
import sys

import requests
from bs4 import BeautifulSoup, Tag
from rich import box
from rich.console import Console
from rich.table import Table, Row


class StockWatcher:
    SEARCH_API = "https://www.screener.in/api/company/search/?q="
    STOCK_DETAILS_API = "https://www.screener.in/"

    def __init__(self):
        self.console = Console()

    def _get_stock_metadata(self, company_name: str):
        query_str = "+".join(company_name.split(" "))
        response = requests.get(self.SEARCH_API + query_str).json()
        return response[0] if len(response) >=1 else None

    def _process(self, ranges_table: Tag):
        tds = ranges_table.findAll("td")
        price_dict = {}
        for i in range(0, len(tds), 2):
            price_dict[tds[i].text] = tds[i + 1].text
        return price_dict

    def get_stock_details(self, company_name: str):
        stock_details = {}
        stock_metadata = self._get_stock_metadata(company_name)
        if stock_metadata is None:
            return None, None
        stock_url = stock_metadata["url"]
        response = requests.get(self.STOCK_DETAILS_API + stock_url)
        bs4 = BeautifulSoup(response.content, "html.parser")
        profit_loss_section = bs4.find("section", {"id": "profit-loss"})

        ratio_section = bs4.find("div", {"id": "top"})
        ratio_list = ratio_section.find("ul", {"id": "top-ratios"}).findAll("li")
        for ratio in ratio_list:
            name = ''.join(ratio.find("span", {"class": "name"}).text.split())
            value = ''.join('/'.join([x.text for x in ratio.findAll('span', {"class": "number"})]).split())
            stock_details[name] = value
        tables = profit_loss_section.findAll("table", {"class": "ranges-table"})

        stock_details["Compounded Sales Growth"] = self._process(tables[0])
        stock_details["Compounded Profit Growth"] = self._process(tables[1])
        stock_details["Stock Price CAGR"] = self._process(tables[2])
        stock_details["Return on Equity"] = self._process(tables[3])
        return stock_metadata['name'], stock_details

    def _format_key(self, colour, key):
        return "[{}]{}[/]".format(colour, key)

    def __format_value(self, value):
        if type(value) == dict:
            return "\n".join("{}  [#ffee00]{}[/]".format(k, v) for k, v in value.items())
        else:
            return str(value)

    def _get_table(self, company_data_dict: dict):
        table = Table(header_style="bold #00e5ff", box=box.SQUARE, show_lines=True)
        if len(company_data_dict) <= 0:
            return None
        table.add_column("Name", style="bold #ff66ff")
        table.add_column("Market Cap", style="bold #ffee00")
        table.add_column("Current Price", style="bold #ffee00")
        table.add_column("High/Low", style="bold #ffee00")
        table.add_column("P/E Ratio", style="bold #ffee00")
        table.add_column("ROCE", style="bold #ffee00")
        table.add_column("Compounded Sales Growth")
        table.add_column("Compounded Profit Growth")
        table.add_column("Stock Price CAGR")
        table.add_column("Return on Equity")

        for company_name, company_data in company_data_dict.items():
            table.add_row(company_name,
                          company_data['MarketCap'],
                          company_data['CurrentPrice'],
                          company_data['High/Low'],
                          company_data['StockP/E'],
                          company_data['ROCE'],
                          self.__format_value(company_data['Compounded Sales Growth']),
                          self.__format_value(company_data['Compounded Profit Growth']),
                          self.__format_value(company_data['Stock Price CAGR']),
                          self.__format_value(company_data['Return on Equity']))

        return table

    def print(self, companies_data_dict: dict):
        table = self._get_table(companies_data_dict)
        if table is None:
            self.console.print("No data found.")
            return
        self.console.print(self._get_table(companies_data_dict))


if __name__ == '__main__':
    stock = StockWatcher()
    companies = sys.argv[1:]
    companies_dict = {}
    for company in companies:
        name, data = stock.get_stock_details(company)
        if name is not None:
            companies_dict[name] = data

    stock.print(companies_dict)
