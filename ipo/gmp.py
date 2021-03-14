import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table


class GMPFetcher:
    console = Console()
    url = "https://www.ipowatch.in/p/ipo-grey-market-premium-latest-ipo-grey.html"

    def __init__(self):
        pass

    def _get_value(self, td):
        return td.find('span').text

    def get_gmp_data(self):
        web_page = requests.get(self.url)
        soup = BeautifulSoup(web_page.content, "html.parser")
        main_div = soup.find("div", {"id": "main-wrapper"})
        table_inside_main_div = main_div.find('table')
        rows = table_inside_main_div.findAll("tr")[1:]
        company_wise_gmp = {}
        for row in rows:
            tds = row.findAll("td")
            company_wise_gmp[self._get_value(tds[0])] = self._get_value(tds[1])

        return company_wise_gmp

    def print_gmp(self, gmp_data: dict):
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Company Name", style="dim")
        table.add_column("Grey Market Premium")

        for company_name, gmp in gmp_data.items():
            table.add_row(company_name, gmp)
        self.console.print(table)


if __name__ == '__main__':
    gmp_fetcher = GMPFetcher()
    print(gmp_fetcher.get_gmp_data())