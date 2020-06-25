import requests
from bs4 import BeautifulSoup
import re
import datetime
import json

rollNo = input('Enter your roll number: ')
pwd = input('Enter your password: ')

begin_time = datetime.datetime.now()

loginurl = 'https://ecampus.psgtech.ac.in/studzone2/'
client = requests.session()
loginResponse = client.get(loginurl)

loginSoup = BeautifulSoup(loginResponse._content, 'html.parser')

viewState = loginSoup.find(id="__VIEWSTATE")['value']
eventValidation = loginSoup.find(id="__EVENTVALIDATION")['value']

homeurl = loginurl + loginSoup.form.get('action')

data = {
    "__VIEWSTATE": viewState,
    "__EVENTVALIDATION": eventValidation,
    "rdolst": "S",
    "txtusercheck": rollNo,
    "txtpwdcheck": pwd,
    "abcd3": "Login"
}

homeResponse = client.post(homeurl, data = data)
homeSoup = BeautifulSoup(homeResponse._content, 'html.parser')
print('Welcome', homeSoup.find(id="Title1_LblStaffName").string)
links = homeSoup.find_all('td')

impLinks = dict()
for link in links:
    if link.get('onclick') is None:
        continue
    impLinks[link.string] = re.findall("href='(.*)'", link.get('onclick'))[0]

# # ordering the sites
# fhand = open('site.txt', 'w')
# for name, link in impLinks.items():
#     space = 35 - len(name)
#     txt = name + ':' + ' ' * space + link + '\n'    
#     fhand.write(txt)
# fhand.close()

# # Wierd Alternatve
# studInfoLoop = CASoup.find(id = 'TbStudInfo').contents
# for i in [1, 3]:
#     for j in [1, 7]:
#         studInfo[studInfoLoop[i].contents[j].string] = studInfoLoop[i].contents[j+4].string

# CA Marks
CAurl = loginurl + impLinks['CA Marks']
CAResponse = client.get(CAurl)
CASoup = BeautifulSoup(CAResponse._content, 'html.parser')

infoTable = CASoup.find(id = 'TbStudInfo')
studInfo = dict()
i = 0
for string in infoTable.stripped_strings:
    if(string == ':'): continue
    if i%2 == 0: 
        key = string
    else:
        studInfo[key] = string
    i = i + 1

markTables = BeautifulSoup(str(list(infoTable.next_siblings)[1]), 'html.parser').findAll('table')

studMarks = list()
for i in range(len(markTables)):
    rowlist = list()
    table = markTables[i]
    if table['id'] == 'TbFootNote': break
    rows = list(table.contents)
    rowCount = 0
    rowHead = list()
    for j in range(len(rows)):
        if rows[j] == '\n': continue
        rowdict = dict()
        if rowCount == 0:
            rowHead = list(rows[j].stripped_strings)
            rowCount = rowCount + 1
            continue
        elif rowCount == 1:
            rowdict = dict(zip(rowHead, ['NaN', 'NaN'] + list(rows[j].stripped_strings)))
        else:
            rowdict = dict(zip(rowHead, list(rows[j].stripped_strings)))
        rowlist.append(rowdict)
        rowCount = rowCount + 1
    studMarks.append(rowlist)

print(json.dumps(studMarks, indent=4))

# Student Attendance
atturl = loginurl + impLinks['Student Attendance']
attResponse = client.get(atturl)
attSoup = BeautifulSoup(attResponse._content, 'html.parser')

studAtt = list()
rowHead = list()

attTable = list(attSoup.find(id = 'PDGcourpercView').contents)
rowCount = 0
for i in range(len(attTable)):
    if(attTable[i] == '\n'): continue
    rows = list(attTable[i].stripped_strings)
    rowdict = dict()
    if rowCount == 0:
        rowHead = rows
    else:
        rowdict = dict(zip(rowHead, rows))
        studAtt.append(rowdict)
    rowCount = rowCount + 1

print(json.dumps(studAtt, indent=4))

print(datetime.datetime.now() - begin_time)