# -*- coding: utf-8 -*-
"""
Created on Tue Mar 12 17:46:26 2024

@author: SJ
"""

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


import time
from datetime import datetime

import os

curr_path = os.path.dirname(os.path.abspath(__file__))

API_URL = "https://api-inference.huggingface.co/models/1-800-BAD-CODE/xlm-roberta_punctuation_fullstop_truecase"
headers = {"Authorization": "Bearer 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"}

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
    url = "https://www.ft.com/cryptofinance?format=rss"
    
    xml_data = requests.get(url).content

    soup = BeautifulSoup(xml_data, "xml")

    res = soup.find_all('item')

    arr = []
    for item in res:
        title = item.find('title').text.strip()
        link = item.find('link').text.strip()
        pub_date = item.find('pubDate').text.strip()
        pub_date = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %Z").date()
        description = item.find('description').text.strip()


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

def scrape_coindesk_rss(no_uid=True):
    url = "https://www.coindesk.com/arc/outboundfeeds/rss/"
    
    xml_data = requests.get(url).content

    soup = BeautifulSoup(xml_data, "xml")

    res = soup.find_all('item')

    arr = []
    
    for item in res:

        title = item.find('title').text.strip()
        description = item.find('description').text.strip()
        link = item.find('link').text.strip()
        pub_date = item.find('pubDate').text.strip()
        pub_date = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z").date()
        article_type = item.find('category', {'domain': 'article-type'}).text.strip()
        if article_type != 'news':
            continue
        uid = len(arr)+1
        obj = {
            'title': title,
            'description': description,
            'pub_date': pub_date,
            'link': link,
            'source': 'CoinDesk'
        }

        if not no_uid: 
            obj['uid'] = uid
        arr.append(obj)
        
    titles = [obj['title'] for obj in arr]
    cleaned_titles = true_case_annotator(titles)

    assert len(titles) == len(cleaned_titles)

    for i in range(len(arr)):
        arr[i]['title'] = cleaned_titles[i]
        
    return arr

def scrape_cointelegraph_rss(no_uid=True):
    # Path to WebDriver (adjust according to your WebDriver path, if necessary)
    # For Chrome

    #driver_path = os.path.join(curr_path, 'webdriver', 'chromedriver_win64', 'chromedriver.exe')
    #service = Service(executable_path=driver_path)
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.implicitly_wait(10)


    # URL of the page to scrape
    url = "https://cointelegraph.com/rss"

    # Open the page
    driver.get(url)

    xml_data = driver.page_source

    # Close the browser
    driver.quit()

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
        description = p_tags[-1].text.strip() if p_tags else description_raw

        uid = len(arr)+1
        obj = {
            'title': title,
            'description': description,
            'pub_date': pub_date,
            'link': link,
            'source': 'Cointelegraph'
        }
        
        if not no_uid: 
            obj['uid'] = uid
        arr.append(obj)
        
    return arr

def scrape_blockchain_news_rss(no_uid=True):

    url = "https://blockchain.news/RSS/"

    xml_data = requests.get(url).content

    soup = BeautifulSoup(xml_data, "xml")

    res = soup.find_all('item')

    arr = []

    for item in res:
        title = item.find('title').text.strip()
        link = item.find('link').text.strip()
        pub_date = item.find('pubDate').text.strip()
        pub_date = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %Z").date()
        description_raw = item.find('description').text.strip()
        parsed_html = BeautifulSoup(description_raw, 'lxml')
        content = None
        for c in parsed_html.body.contents:
            if isinstance(c, str):
                content = c
        description = description_raw if not content else content
        uid = len(arr)+1
        obj = {
            'title': title,
            'description': description,
            'pub_date': pub_date,
            'link': link,
            'source': 'Blockchain News'
        }
        
        if not no_uid: 
            obj['uid'] = uid
        arr.append(obj)

    titles = [obj['title'] for obj in arr]
    cleaned_titles = true_case_annotator(titles)

    assert len(titles) == len(cleaned_titles)

    for i in range(len(arr)):
        arr[i]['title'] = cleaned_titles[i]
        
    return arr

def scrape_blockworks_rss(no_uid = True):

    url = "https://blockworks.co/feed"

    xml_data = requests.get(url).content

    soup = BeautifulSoup(xml_data, "xml")

    res = soup.find_all('entry')

    arr = []

    for item in res:
        cat_include = ['Finance','Policy','DeFi','Business']
        cat_omit = ['Op-Ed', 'Podcast', 'Education', 'Analysis', 'Sponsored']

        title = item.find('title').text.strip()
        link = item.find('id').text.strip()
        pub_date = item.find('published').text.strip()

        if not pub_date:
            continue
        pub_date = datetime.strptime(pub_date, "%Y-%m-%dT%H:%M:%S.%fZ").date()

        categories = item.find_all('category')

        has_cat_include = False
        has_cat_omit = False
        for c in categories:
            if c['label'].strip() in cat_omit:
                has_cat_omit = True

            if c['label'].strip() in cat_include:
                has_cat_include=True

        if has_cat_omit or not has_cat_include:
            continue

        description = item.find('summary').text.strip() + '.' # Typically ends without a full stop, but might change in the future

        uid = len(arr)+1
        obj = {
            'title': title,
            'description': description,
            'pub_date': pub_date,
            'link': link,
            'source': 'Blockworks'
        }

        if not no_uid: 
            obj['uid'] = uid
        arr.append(obj)

    return arr

def rss_scraper(omit):
    to_scrape = ['Cointelegraph', 'CoinDesk', 'Blockchain News', 'Blockworks', 'Financial Times']
    source_to_scraper_mapper = {'Cointelegraph': scrape_cointelegraph_rss(), 'CoinDesk': scrape_coindesk_rss(), 
                                'Blockchain News': scrape_blockchain_news_rss(), 'Blockworks': scrape_blockworks_rss(), "Financial Times": scrape_ft_rss()}
    for source in to_scrape:
        if source in omit: 
            to_scrape.remove(source)
            
    news_df = pd.DataFrame()
    
    for source in to_scrape:
        arr_of_obj = source_to_scraper_mapper[source]
        df = pd.DataFrame(arr_of_obj)
        news_df = pd.concat([news_df, df])
    
    return news_df.reset_index(drop=True).drop_duplicates(subset='title')
        
def generate_curated_news(curr_date_str, earliest_date_str=None, omit=[]):
    df = rss_scraper(omit)
    if earliest_date_str is not None:
        df = df[df['pub_date']>=datetime.strptime(earliest_date_str, "%d %b %Y").date()]
    df = df.sort_values('title')
    return df, curr_date_str
