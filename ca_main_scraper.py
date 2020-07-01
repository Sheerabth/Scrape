import asyncio
import aiohttp
from bs4 import BeautifulSoup


class CAMainScraper:
    login_paage_url = 'https://ecampus.psgtech.ac.in/studzone2/'
    ca_main_url = f'{login_paage_url}AttWfPercView.aspx'

    def __init__(self, cookies):
        self._cookies = cookies

    async def scrape_ca_main(self):
        async with aiohttp.request("get", CAMainScraper.ca_main_url, cookies=self._cookies) as ca_main_request:
            binary_content = await ca_main_request.read()
            ca_main_page = binary_content.decode()
        ca_main_soup = BeautifulSoup(ca_main_page, 'html.parser')
        # TODO: Redo / Increase efficiency and understanability
        mark_tables = BeautifulSoup(str(list(ca_main_soup.find(id='TbStudInfo').next_siblings)), 'html.parser').findAll('table')
        mark_tables.pop()

        stud_marks = list()
        for i in range(len(mark_tables)):
            row_list = list()
            table = mark_tables[i]
            if table['id'] == 'TbFootNote':
                break
            rows = list(table.contents)
            for j in range(len(rows)):
                if rows[j] == '\n':
                    continue
                row_list.append(list(rows[j].stripped_strings))
            stud_marks.append(row_list)
        print(stud_marks)
