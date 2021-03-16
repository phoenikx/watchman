from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table


class SubscriptionWatcher:
    console = Console()
    url = "https://www.chittorgarh.com/report/ipo-subscription-status-live-bidding-data-bse-nse/21/?sort=&page=&year={}"

    def __init__(self):
        self.url = str.format(self.url, datetime.now().year)

    def _add_colour(self, color, obj):
        return f'[{color}] {str(obj)} [/]'

    def _format(self, obj):
        if not obj:
            return None
        color = "red"
        try:
            end_date = datetime.strptime(obj, '%b %d, %Y')
            if (end_date + timedelta(hours=16) - datetime.now()).total_seconds() > 0:
                color = "green"
            return self._add_colour(color, end_date.date())
        except:
            number = float(obj)
            if number > 10:
                color = "#F5F5F5"
            return self._add_colour(color, str(number))

    def get_subscription_table(self):
        subscription_table = Table(header_style="bold cyan", show_lines=True)
        web_page = requests.get(self.url)
        soup = BeautifulSoup(web_page.content, "html.parser")
        div_table = soup.find("div", {"id": "report_data"}).find('table')
        columns = [x.text for x in div_table.find('thead').findAll('a')]
        [subscription_table.add_column(column) for column in columns]
        rows = div_table.find('tbody').findAll('tr')
        for row in rows:
            cells = row.findAll('td')
            cells_data = []
            for i in range(len(cells)):
                link = cells[i].find('a')
                if link is not None:
                    cells_data.append(self._add_colour('#F5F5F5', link.text))
                else:
                    formatted_text = self._format(cells[i].text)
                    cells_data.append(formatted_text if formatted_text else "-")
            subscription_table.add_row(*[str(x) for x in cells_data])

        return subscription_table

    def print_subscription_table(self, table):
        self.console.print(table)


if __name__ == '__main__':
    subscription_watcher = SubscriptionWatcher()
    table = subscription_watcher.get_subscription_table()
    subscription_watcher.print_subscription_table(table)