import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re
from typing import List, Tuple

import exceptions


class StudzoneScraper:
    login_page_url = 'https://ecampus.psgtech.ac.in/studzone2/'
    home_page_url = f'{login_page_url}AttWfStudMenu.aspx'
    ca_main_url = f'{login_page_url}CAMarks_View.aspx'

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.logged_in = False
        self._cookies = {}

    async def __get_login_form_and_url__(self) -> Tuple[dict, str]:
        async with aiohttp.request("get", StudzoneScraper.login_page_url) as login_page_request:
            binary_content = await login_page_request.read()
            login_page = binary_content.decode()

        # Parsing HTML for required values
        login_soup = BeautifulSoup(login_page, 'html.parser')
        view_state = login_soup.find(id="__VIEWSTATE")['value']
        event_validation = login_soup.find(id="__EVENTVALIDATION")['value']
        action_url = StudzoneScraper.login_page_url + login_soup.form.get('action')

        # Reconstructing the form data for POST request
        form_data = {
            "__VIEWSTATE": view_state,
            "__EVENTVALIDATION": event_validation,
            "rdolst": "S",
            "txtusercheck": self.username,
            "txtpwdcheck": self.password,
            "abcd3": "Login"
        }
        return form_data, action_url

    async def login(self):
        # A session is used to retrieved the required cookies
        session = aiohttp.ClientSession()
        form_data, action_url = await self.__get_login_form_and_url__()

        # Sending Login POST request and decoding response
        login_request = await session.post(action_url, data=form_data)
        binary_content = await login_request.read()
        login_response = binary_content.decode()

        # Storing the cookies in the current instance and closing session
        for cookie in session.cookie_jar:
            cookie_key = cookie.key
            cookie_value = cookie.value
            self._cookies[cookie_key] = cookie_value
        await session.close()

        # Parse Response to check is Login was successful
        login_response_soup = BeautifulSoup(login_response, 'html.parser')
        try:
            login_response_soup.find(id="Title1_LblStaffName")
            self.logged_in = True
        except AttributeError:
            script_tags = list(login_response_soup.find_all('script'))
            if script_tags[0].string.strip() == "alert( ' Invalid Password' )":
                raise exceptions.InvalidPasswordError(f"Invalid Password for {self.username}!")
            elif script_tags[len(script_tags) - 1].string.strip() == "alert('Invalid Login Id')":
                raise exceptions.InvalidUsernameError(f"{self.username} is not a valid Login ID!")
            else:
                raise exceptions.InvalidCredentialsError("Unknown Exception")  # TODO: log the HTML and set up a alert

    async def __login_check_(self):
        # TODO: Try to get the Home Menu Page with cookies and check for redirects in responses
        raise NotImplementedError

    async def scrape_stud_info(self):
        if self.logged_in:
            async with aiohttp.request("get", StudzoneScraper.ca_main_url, cookies=self._cookies) as ca_main_request:
                binary_content = await ca_main_request.read()
                ca_main_page = binary_content.decode()
            ca_main_soup = BeautifulSoup(ca_main_page, 'html.parser')

            # Parsing for Student Info
            info_table = ca_main_soup.find(id='TbStudInfo')
            print(info_table)
            stud_info = {}
            i = 0  # TODO: Redo / Increase efficiency and understanability
            for string in info_table.stripped_strings:
                if string == ':':
                    continue
                if i % 2 == 0:
                    key = string
                else:
                    stud_info[key] = string
                i = i + 1

            print(stud_info)


async def main():
    obj = StudzoneScraper("19pw08", '16dec01')
    await obj.login()
    await obj.scrape_ca_main()


asyncio.run(main())
