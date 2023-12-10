from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import re
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

key_word = '胖才可愛'
item_max = 5  # the maximum number of result you want to save
wait_max = 10  # the maximum seconds waiting for the element appearing

main_url = 'https://store.line.me/home/zh-Hant'  # main page url

current_dir = os.path.dirname(os.path.abspath(__file__))  # the directory of this program

# setup the chrome driver
s = Service(ChromeDriverManager().install())
chrome_options = webdriver.ChromeOptions() 
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])  # disable showing "DevTools listening" from selenium
driver = webdriver.Chrome(service=s, options=chrome_options)
driver.maximize_window()
driver.get(main_url)
time.sleep(1)

# input the keyword
input_keyword = WebDriverWait(driver, wait_max).until(EC.presence_of_element_located((By.CLASS_NAME, 'FnSearchInput')))
input_keyword.send_keys(key_word)
time.sleep(0.5)

# press the "search" button
btn_search = WebDriverWait(driver, wait_max).until(EC.presence_of_element_located((By.CLASS_NAME, 'FnSearchIcon')))
btn_search.click()
time.sleep(1)

# get the url of each result
search_result_list = WebDriverWait(driver, wait_max).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'ul[data-test="search-sticker-item-list"]')))
result_url_list = [result.get_attribute('href') for result in search_result_list.find_elements(By.TAG_NAME, 'a')]
time.sleep(0.5)

# iterate through the item for a maximum of item_max times and store the images on the website
for item_index in range(item_max):
    if item_index == len(result_url_list): break
    url = result_url_list[item_index]
    driver.get(url)
    title = WebDriverWait(driver, wait_max).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'p[data-test="sticker-name-title"]'))).text.strip()
    print('\n', title)
    
    img_item_list = WebDriverWait(driver, wait_max).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'mdCMN09LiInner.FnImage')))
    img_url_list = [image_item.find_element(By.TAG_NAME, 'span').get_attribute('style') for image_item in img_item_list]
    img_url_list = [re.search(r'url\(["\']?(.*?)["\']?\)', img_url).group(1) for img_url in img_url_list]
    
    # save images to the certain directory
    for index, img_url in enumerate(img_url_list):
        if img_url != None: img_response = requests.get(img_url)  # avoid the url doesn't exist
        # confirm the content of each url are grabed successfully
        if img_response.status_code == 200:
            img_dir = os.path.join(current_dir, f'{sanitize_path_name(title)}')
            os.makedirs(img_dir, exist_ok=True)  # create all the required directories
            
            img_path = os.path.join(img_dir, f'img_{index + 1}.jpg')  # give a index to each image
            
            # save the image
            with open(img_path, 'wb') as file:
                file.write(img_response.content)
        else:
            print(f'Failed to retrieve image from {img_url}. Status code: {img_response.status_code}')
    

# close the chrome driver
driver.quit()

print('\nProgram Finished.')
