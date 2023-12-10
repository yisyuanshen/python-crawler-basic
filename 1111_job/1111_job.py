from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import os

key_word = 'SOFTWARE ENGINEER'
scroll_down_times = 3  # the times the page scrolling down
wait_max = 10  # the maximum seconds waiting for the element appearing

main_url = 'https://www.1111.com.tw/'  # main page url

# setup the chrome driver
s = Service(ChromeDriverManager().install())
chrome_options = webdriver.ChromeOptions() 
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])  # disable showing "DevTools listening" from selenium
driver = webdriver.Chrome(service=s, options=chrome_options)
driver.maximize_window()
driver.get(main_url)
time.sleep(1)

# click the button of area list
btn_area_list = WebDriverWait(driver, wait_max).until(EC.presence_of_element_located((By.XPATH, '//a[@data-target="#searchLocation"]')))
btn_area_list.click()
time.sleep(0.5)

# click the checbox of "Taipei"
checkbox_taipei = WebDriverWait(driver, wait_max).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[k="100100"][data-count="0"]')))
checkbox_taipei.click()
time.sleep(0.5)

# click the checbox of "Daan District"
checkbox_daan =  WebDriverWait(driver, wait_max).until(EC.presence_of_element_located((By.XPATH, '//label[@k="100105"]')))
checkbox_daan.click()
time.sleep(0.5)

# click the "confirmation" button
btn_area_confirm =  WebDriverWait(driver, wait_max).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button[onclick="tCodeMenu.enter()"]')))
btn_area_confirm.click()
time.sleep(0.5)

# input the keyword
input_keyword = WebDriverWait(driver, wait_max).until(EC.presence_of_element_located((By.ID, 'ks')))
input_keyword.send_keys(key_word)
time.sleep(0.5)

# click the "search" button
btn_search = WebDriverWait(driver, wait_max).until(EC.presence_of_element_located((By.CLASS_NAME, 'btn-search')))
btn_search.click()
time.sleep(1)


# scroll down to make more elements appear
for times in range(scroll_down_times):
    scroll_position = driver.execute_script("return document.body.scrollHeight;")*2/3
    driver.execute_script(f'window.scrollTo(0, {scroll_position});')
    time.sleep(2)

time.sleep(1)

# find all job items, and append all the links into a list
search_result_list = driver.find_elements(By.CSS_SELECTOR, 'div.item__job.job_item')
job_url_list = []

for search_result in search_result_list:
    job_title = search_result.find_element(By.CLASS_NAME, 'job_item_info').find_element(By.TAG_NAME, 'a')
    job_url_list.append(job_title.get_attribute('href'))

# create a result dictionary, browse all the links, and add information about each job
result_dict = {'Job Title': [], 'Company': [], 'Description': [], 'Info': [], 'Skill': [], 'Url': []}
for url in job_url_list:
    driver.get(url)
    
    # find areas containing different information
    job_title = WebDriverWait(driver, wait_max).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class="ui_card_top sticky-top"]')))
    company = WebDriverWait(driver, wait_max).until(EC.presence_of_element_located((By.CLASS_NAME, 'ui_card_company_link')))
    description = WebDriverWait(driver, wait_max).until(EC.presence_of_element_located((By.CLASS_NAME, 'job_description')))
    info = WebDriverWait(driver, wait_max).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class="content_items job_info"]')))
    skill = WebDriverWait(driver, wait_max).until(EC.presence_of_element_located((By.CLASS_NAME, 'job_skill')))

    result_dict['Job Title'].append(job_title.text.replace('\n', ' '))
    result_dict['Company'].append(company.text.replace('\n', ' '))
    result_dict['Description'].append(description.text.replace('\n', ' '))
    result_dict['Info'].append(info.text.replace('\n', ' '))
    result_dict['Skill'].append(skill.text.replace('\n', ' '))
    result_dict['Url'].append(url)

    # print results in the terminal
    print('='*30, '\n')
    print(job_title.text.replace('\n', ' '), '\n')
    print(company.text.replace('\n', ' '), '\n')
    print(description.text.replace('\n', ' '), '\n')

# close the chrome driver
driver.quit()

# save the result in the same directory as this program's
current_dir = os.path.dirname(os.path.abspath(__file__))
result_file_path = os.path.join(current_dir, '1111_job_result.xlsx')
pd.DataFrame(result_dict).to_excel(result_file_path, index=False)

print('Program Finished.')
