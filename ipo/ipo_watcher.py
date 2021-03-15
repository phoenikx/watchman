import os
from datetime import datetime

import requests
from rich.console import Console
from rich.table import Table

from ipo.gmp import GMPFetcher


class IPOWatcher:
    url = 'https://console.zerodha.com/api/ipo'
    COOKIE_KEY = 'COOKIE'
    console = Console()

    def __init__(self):
        pass

    def _get_open_listings(self):
        cookie = os.environ[self.COOKIE_KEY]
        if cookie is None:
            raise ValueError("Cookie not set in environment, please try again with a valid cookie.")

        return requests.get(self.url, headers={'cookie': cookie}).json()

    def _apply_colour(self, colour, string):
        return f'[{colour}] {str(string)} [/]'

    def _print_formatted_output(self, ipo_data):
        table = Table(show_header=True, header_style="bold cyan", show_lines=True)
        table.add_column("Company")
        table.add_column("Subscription starts")
        table.add_column("Subscription ends")
        table.add_column("Listing date")
        table.add_column("Min price")
        table.add_column("Max price")
        table.add_column("Min. Qty")
        table.add_column("Funds Required")
        table.add_column('Time left')

        for company in ipo_data['data']['result']:
            company_name = company["company_name"]
            bidding_start_date = datetime.fromisoformat(company["bidding_start_date"])
            bidding_end_date = datetime.fromisoformat(company["bidding_end_date"])
            listing_date = datetime.fromisoformat(company["listing_date"])
            min_price = company["min_price"]
            max_price = company["max_price"]
            min_bid_qty = company['min_bid_quantity']
            funds_reqd = max_price * min_bid_qty
            time_left = bidding_end_date - datetime.now()
            colour = "grey"
            if time_left.total_seconds() > 0:
                colour = "green"
            elif listing_date < datetime.now():
                colour = "red"

            table.add_row(self._apply_colour(colour, company_name),
                          self._apply_colour(colour, str(bidding_start_date.date())),
                          self._apply_colour(colour, str(bidding_end_date.date())),
                          self._apply_colour(colour, str(listing_date.date())),
                          self._apply_colour(colour, str(min_price)),
                          self._apply_colour(colour, str(max_price)),
                          self._apply_colour(colour, str(min_bid_qty)),
                          self._apply_colour(colour, str(funds_reqd)),
                          self._apply_colour(colour, time_left))
        self.console.print(table)

    def print_open_listings(self):
        open_listings = self._get_open_listings()
        self._print_formatted_output(open_listings)


if __name__ == '__main__':
    ipo_watcher = IPOWatcher()
    gmp_fetcher = GMPFetcher()
    gmp_data = gmp_fetcher.get_gmp_data()
    ipo_watcher.print_open_listings()
    gmp_fetcher.print_gmp(gmp_data)
