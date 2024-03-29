from bs4 import BeautifulSoup
from bs4.element import Comment
import pandas as pd
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType


import time
from datetime import datetime

import os
import shutil
import subprocess

curr_path = os.path.dirname(os.path.abspath(__file__))

API_URL = "https://api-inference.huggingface.co/models/1-800-BAD-CODE/xlm-roberta_punctuation_fullstop_truecase"
headers = {"Authorization": ""}

def get_chromedriver_path() -> str:
    return shutil.which('chromedriver')

def hf_query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()

def true_case_annotator(original_texts):
    inputs = """"""
    for i in range(len(original_texts)):
        original_texts[i] = original_texts[i].lower()
        inputs = inputs + original_texts[i] + '<ZXCSDZ>.'
    output = hf_query({"inputs":inputs})
    if 'error' in output:
        return False
    output = output[0]['generated_text']
    output_arr = output.split('<ZXCSDZ>.')[:-1]
    output_arr = [ele.replace("\\n", "").strip().strip('.') for ele in output_arr]

    return output_arr

def scrape_ft_rss(no_uid=True):
    url = "https://www.ft.com/artificial-intelligence?format=rss"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    
    xml_data = requests.get(url,headers=headers).content
    soup = BeautifulSoup(xml_data, "xml")

    res = soup.find_all('item')

    arr = []
    for item in res:
        title = item.find('title').text.strip()
        link = item.find('link').text.strip()
        pub_date = item.find('pubDate').text.strip()
        pub_date = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %Z").date()
        description = item.find('description').text.strip()
        description = description + '.' if len(description)>0 and description[-1] != '.' else description


        uid = len(arr)+1
        obj = {
            'title': title,
            'description': description,
            'pub_date': pub_date,
            'link': link,
            'source': 'Financial Times'
        }
        
        if not no_uid: 
            obj['uid'] = uid
        arr.append(obj)
        
    return arr

def scrape_mitnews_rss(no_uid=True):
    url = "https://www.ft.com/artificial-intelligence?format=rss"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    
    xml_data = requests.get(url,headers=headers).content
    soup = BeautifulSoup(xml_data, "xml")

    res = soup.find_all('item')

    arr = []
    for item in res:
        title = item.find('title').text.strip()
        link = item.find('link').text.strip()
        pub_date = item.find('pubDate').text.strip()
        pub_date = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %Z").date()
        description = item.find('description').text.strip()
        description = description + '.' if len(description)>0 and description[-1] != '.' else description

        uid = len(arr)+1
        obj = {
            'title': title,
            'description': description,
            'pub_date': pub_date,
            'link': link,
            'source': 'MIT News'
        }
        
        if not no_uid: 
            obj['uid'] = uid
        arr.append(obj)
        
    return arr

def scrape_venturebeat_rss(no_uid=True):
    url = "https://venturebeat.com/category/ai/feed"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    
    xml_data = requests.get(url,headers=headers).content
    soup = BeautifulSoup(xml_data, "xml")

    res = soup.find_all('item')

    arr = []
    for item in res:
        title = item.find('title').text.strip()
        link = item.find('link').text.strip()
        pub_date = item.find('pubDate').text.strip()
        pub_date = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z").date()
        description = item.find('description').text.strip()


        uid = len(arr)+1
        obj = {
            'title': title,
            'description': description,
            'pub_date': pub_date,
            'link': link,
            'source': 'VentureBeat'
        }
        
        if not no_uid: 
            obj['uid'] = uid
        arr.append(obj)
        
    return arr

def scrape_techcrunch_rss(no_uid=True):
    url = "https://techcrunch.com/feed"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    
    xml_data = requests.get(url,headers=headers).content
    soup = BeautifulSoup(xml_data, "xml")

    res = soup.find_all('item')

    arr = []
    for item in res:
        title = item.find('title').text.strip()
        link = item.find('link').text.strip()
        pub_date = item.find('pubDate').text.strip()
        pub_date = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z").date()
        description_raw = item.find('description').text.strip()
        parsed_html = BeautifulSoup(description_raw, 'lxml')
        p_tags = parsed_html.find_all('p')
        description = p_tags[0].text.strip() if p_tags else description_raw


        uid = len(arr)+1
        obj = {
            'title': title,
            'description': description,
            'pub_date': pub_date,
            'link': link,
            'source': 'TechCrunch'
        }
        
        if not no_uid: 
            obj['uid'] = uid
        arr.append(obj)
        
    return arr

def rss_scraper(omit):
    to_scrape = ['VentureBeat', 'TechCrunch', 'Financial Times', 'MIT News']
    source_to_scraper_mapper = {'VentureBeat': scrape_venturebeat_rss(), 'TechCrunch': scrape_techcrunch_rss(), 
                                'Financial Times': scrape_ft_rss(), 'MIT News': scrape_mitnews_rss()}
    for source in to_scrape:
        if source in omit: 
            to_scrape.remove(source)
            
    news_df = pd.DataFrame()
    
    for source in to_scrape:
        arr_of_obj = source_to_scraper_mapper[source]
        df = pd.DataFrame(arr_of_obj)
        news_df = pd.concat([news_df, df])
    news_df = news_df[news_df['description'].str.len() > 25]
    return news_df.reset_index(drop=True).drop_duplicates(subset='title')
        
def generate_curated_news(curr_date_str, earliest_date_str=None, omit=[]):
    df = rss_scraper(omit)
    if earliest_date_str is not None:
        df = df[df['pub_date']>=datetime.strptime(earliest_date_str, "%d %b %Y").date()]
    df = df.sort_values('title').reset_index(drop=True)
    return df, curr_date_str