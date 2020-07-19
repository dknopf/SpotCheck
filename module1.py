from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options  # for suppressing the browser head
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import concurrent.futures
import re
import time
from datetime import datetime
import json
import atexit
import pandas as pd
import multiprocessing as mp
import os
import sys
from pathlib import Path
"""
Creates a webdriver to run the scraping in
"""
options = webdriver.ChromeOptions()
options.add_argument('--no-proxy-server')
options.add_argument('headless')
options.add_argument('log-level=3') # Suppresses error messages


path = 'C:/Users/daniel/Downloads/chromedriver_win32/chromedriver.exe'


main_driver = webdriver.Chrome(executable_path=path, options=options)
alpha_driver = webdriver.Chrome(executable_path=path, options=options)
individual_driver = webdriver.Chrome(executable_path=path, options=options)

final_dict = {}

alpha_driver.get('https://owaprod-pub.wesleyan.edu/reg/!wesmaps_page.html?stuid=&facid=NONE&crse_list=ENGL&term=1209&offered=Y#fall')
table_block = alpha_driver.find_element(By.XPATH, '/html/body/table/tbody/tr[2]/td/table[1]/tbody')
links = table_block.find_elements(By.XPATH, '//a[contains(text(), "ENGL"))]')
for link in links:
    title = individual_driver.find_element(By.XPATH, '//span[@class="title]').text
    final_dict[title] = []
    individual_driver.get(link.get_attribute('href'))
    statuses = individual_driver.find_elements(By.XPATH, '//a[contains(text(), "Instruction")]')
    for status in statuses:
        final_dict[title].append(status.text)

print(final_dict)