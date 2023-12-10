from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import re
import pandas as pd
import time
import os

# remove illegal characters in the path name
def sanitize_path_name(path_name):
    # characters to be removed
    illegal_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in illegal_chars:
        path_name = path_name.replace(char, '')
        
    # strip leading/trailing whitespace and periods
    path_name = path_name.strip().strip('.')
    
    # replace ASCII control characters
    path_name = re.sub(r'[\000-\037]', '', path_name)
    
    return path_name


key_word = '停車位'
page_max = 50  # the maximum pages you want to search for
wait_max = 10  # the maximum seconds waiting for the element appearing

main_url = 'https://rent.591.com.tw/'  # main page url

current_dir = os.path.dirname(os.path.abspath(__file__))  # the directory of this program
result_dict = {'Title': [], 'Url': [], 'Tags': [], 'Style': [], 'Area': [], 'Tip': [], 'Msg': [], 'Price': []}

# setup the chrome driver
s = Service(ChromeDriverManager().install())
chrome_options = webdriver.ChromeOptions() 
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])  # disable showing "DevTools listening" from selenium
driver = webdriver.Chrome(service=s, options=chrome_options)
driver.maximize_window()
driver.get(main_url)
time.sleep(1)

# input the keyword
input_keyword = WebDriverWait(driver, wait_max).until(EC.presence_of_element_located((By.CLASS_NAME, 'searchInput')))
input_keyword.send_keys(key_word)
time.sleep(0.5)

# press the "search" button
btn_search = WebDriverWait(driver, wait_max).until(EC.presence_of_element_located((By.CLASS_NAME, 'searchBtn')))
btn_search.click()
time.sleep(3)

# browse each page to get the information of search results
for page in range(page_max):
    search_result_list = WebDriverWait(driver, wait_max).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'vue-list-rent-item')))
    
    # append all the information of the each result into a dictionary
    for search_result in search_result_list:
        url = search_result.find_element(By.TAG_NAME, 'a').get_attribute('href')
        title = search_result.find_element(By.CLASS_NAME, 'item-title').text
        tags = search_result.find_element(By.CLASS_NAME, 'item-tags').text
        style = search_result.find_element(By.CLASS_NAME, 'item-style').text
        area = search_result.find_element(By.CLASS_NAME, 'item-area').text
        tip = search_result.find_element(By.CLASS_NAME, 'item-tip').text
        msg = search_result.find_element(By.CLASS_NAME, 'item-msg').text
        price = search_result.find_element(By.CLASS_NAME, 'item-price').text
        
        result_dict['Title'].append(title)
        result_dict['Url'].append(url)
        result_dict['Tags'].append(tags)
        result_dict['Style'].append(style)
        result_dict['Area'].append(area)
        result_dict['Tip'].append(tip)
        result_dict['Msg'].append(msg)
        result_dict['Price'].append(price)
        
        # get image urls of each result
        img_item_list = WebDriverWait(search_result, wait_max).until(EC.presence_of_element_located((By.CLASS_NAME, 'carousel-list'))).find_elements(By.TAG_NAME, 'li')
        img_url_list = [image_item.find_element(By.TAG_NAME, 'img').get_attribute('data-original') for image_item in img_item_list]
        
        # save images to the certain directory
        for index, img_url in enumerate(img_url_list):
            if img_url != None: img_response = requests.get(img_url)  # avoid the url doesn't exist
            # confirm the content of each url are grabed successfully
            if img_response.status_code == 200:
                img_dir = os.path.join(current_dir, f'img\\{sanitize_path_name(title)}')
                os.makedirs(img_dir, exist_ok=True)  # create all the required directories
                 
                img_path = os.path.join(img_dir, f'img_{index + 1}.jpg')  # give a index to each image
                
                # save the image
                with open(img_path, 'wb') as file:
                    file.write(img_response.content)
            else:
                print(f'Failed to retrieve image from {img_url}. Status code: {img_response.status_code}')
            
        print(f'\n{title}')
    
    # find the "Next Page" button
    btn_next_page = WebDriverWait(driver, wait_max).until(EC.presence_of_element_located((By.CLASS_NAME, 'pageNext')))
    
    # check the current page is not the last one (if so, the class name of the "Next Page" button will contain "last")
    if 'last' in btn_next_page.get_attribute('class'):
        print('\nNo enough pages')
        break
    
    # press the "Next Page" button
    btn_next_page.click()
    time.sleep(1)

# close the chrome driver
driver.quit()

# save the result to an excel file
result_file_path = os.path.join(current_dir, '591_rent_result.xlsx')
pd.DataFrame(result_dict).to_excel(result_file_path, index=False)

print('\nProgram Finished.')
