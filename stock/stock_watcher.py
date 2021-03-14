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
        profit_and_loss = {}
        stock_metadata = self._get_stock_metadata(company_name)
        if stock_metadata is None:
            return None
        stock_url = stock_metadata["url"]
        response = requests.get(self.STOCK_DETAILS_API + stock_url)
        bs4 = BeautifulSoup(response.content, "html.parser")
        profit_loss_section = bs4.find("section", {"id": "profit-loss"})
        tables = profit_loss_section.findAll("table", {"class": "ranges-table"})

        profit_and_loss["compounded_sales_growth"] = self._process(tables[0])
        profit_and_loss["compounded_profit_growth"] = self._process(tables[1])
        profit_and_loss["stock_price_cagr"] = self._process(tables[2])
        profit_and_loss["return_on_equity"] = self._process(tables[3])
        return stock_metadata['name'], profit_and_loss

    def _format_key(self, colour, key):
        return "[{}]{}[/]".format(colour, key)

    def __format_value(self, value_dict: dict):
        return "\n".join("{}  [yellow]{}[/]".format(k, v) for k, v in value_dict.items())

    def _get_table(self, company_data: dict):
        table = Table(header_style="bold cyan", box=box.SQUARE, show_lines=True)
        table.add_column("Name")
        table.add_column("Compounded Sales Growth")
        table.add_column("Compounded Profit Growth")
        table.add_column("Stock Price CAGR")
        table.add_column("Return on Equity")
        for company_name, company_data in company_data.items():
            if company_data is None:
                continue
            table.add_row(*[self._format_key("grey", company_name),
                            self._format_key("grey", self.__format_value(company_data['compounded_sales_growth'])),
                            self._format_key("grey", self.__format_value(company_data['compounded_profit_growth'])),
                            self._format_key("grey", self.__format_value(company_data['stock_price_cagr'])),
                            self._format_key("grey", self.__format_value(company_data['return_on_equity']))])
        return table

    def print(self, companies_data_dict: dict):
        self.console.print(self._get_table(companies_data_dict))


if __name__ == '__main__':
    stock = StockWatcher()
    companies = sys.argv[1:]
    companies_dict = {}
    for company in companies:
        name, data = stock.get_stock_details(company)
        companies_dict[name] = data

    stock.print(companies_dict)
