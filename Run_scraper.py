import requests
from bs4 import BeautifulSoup
import re, os
import pandas as pd
from tqdm import tqdm
import pandas as pd
import time

Broken_links = []
def is_match(string):
    pass_matches = ['Senate;','House of Representatives;','NOTIFICATION OF REASSEMBLING OF CONGRESS;','PRAYER;','THE JOURNAL;',"PLEDGE OF ALLEGIANCE;",
               "(APPOINTMENT (AS|TO) MEMBERS (TO|OF))","COMMUNICATION FROM",'ANNOUNCEMENT BY THE','PERSONAL EXPLANATION',
               'LEGISLATIVE PROGRAM;',"ADJOURNMENT","EXECUTIVE COMMUNICATION",'REPORT ON','PUBLIC BILLS AND RESOLUTIONS',
               'MEMORIALS;',"ADDITIONAL SPONSORS;","PETITIONS,",'REPORT TO','SUPPLEMENTAL APPROPRIATIONS;','RECESS','AFTER RECESS',
               'DISPENSING WITH CALENDAR','SPECIAL ORDERS GRANTED','EXTENSIONS OF REMARKS','OATH OF OFFICE','TIME LIMITATION',
               'PUBLIC BILLS AND RESOLUTIONS','BILLS AND JOINT RESOLUTIONS','MESSAGE FROM THE ','GENERAL LEAVE','REMOVAL OF NAME OF MEMBER','REQUEST TO POSTPONE',
               'REPORTS OF COMMITTEE','Constitutional Authority Statement','DESIGNATION OF','EXPENDITURE REPORTS CONCERNING',
                'BILL AND RESOLUTION','LEAVE OF ABSENCE']

    matched = False
    for match in pass_matches:
        if re.findall(match,string):
            matched = True
    return matched

def get_house_record(link):
    url = requests.get('https://www.congress.gov' + link['href'])
    if url.status_code == 200:
        record_soup = BeautifulSoup(url.text,'html.parser')
        table = record_soup.find('table',class_='item_table').find('tbody')
        links = [t.find('td').find('a') for t in table.find_all('tr')]
        links_ = [(link['href'], link.text) for link in links if not is_match(link.text)]
        return links_
    else:
        Broken_links.append({"url":link,"code":url.status_code})
        return []

def get_all_text(link):
    try:
        date = re.findall('(?<=congressional-record\/)([0-9]{4}\/[0-9]{2}\/[0-9]{2})\/(?=house)',link[0])[0]
    except:
        date = link[0]
    text_page = requests.get('https://www.congress.gov'+link[0])
    if text_page.status_code == 200:
        parsed = BeautifulSoup(text_page.text,'html.parser')
        return {"date":date,'title':link[1],'text':parsed.find('pre').text}
    else:
        Broken_links.append({"url":link,"code":url.status_code})

lists = [f"{i}th" for i in range(112,117)]
for congress in lists:
    base_url = f'https://www.congress.gov/congressional-record/{congress}-congress/browse-by-date'
    base_text = requests.get(base_url).text
    soup_base = BeautifulSoup(base_text,'html.parser')

    section_links = soup_base.find_all('a',href=re.compile('.*house-section'))

    total_list = []
    for link in tqdm(section_links):
        total_list.append(get_house_record(link))
    print(f"Broken Links = {len(Broken_links)}")

    flat_links = [link for sublist in total_list for link in sublist]

    _texts = []
    for l in tqdm(flat_links):
        _texts.append(get_all_text(l))

    df = pd.DataFrame(_texts)
    df.to_csv(f'{congress}_nonLegislative.csv')
    print(f'saved {congress} to disc')
