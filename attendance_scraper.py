import asyncio
import aiohttp
from bs4 import BeautifulSoup


class AttendanceScraper:
    login_paage_url = 'https://ecampus.psgtech.ac.in/studzone2/'
    att_url = f'{login_paage_url}AttWfPercView.aspx'

    def __init__(self, cookies):
        self._cookies = cookies

    async def scrape_attendace(self):
        async with aiohttp.request("get", AttendanceScraper.att_url, cookies=self._cookies) as att_request:
            binary_content = await att_request.read()
            att_page = binary_content.decode()
        att_soup = BeautifulSoup(att_page, 'html.parser')

        stud_att = list()
        att_table = list(att_soup.find(id='PDGcourpercView').contents)
        for i in range(len(att_table)):
            if att_table[i] == '\n':
                continue
            row = list(att_table[i].stripped_strings)
            stud_att.append(row)
