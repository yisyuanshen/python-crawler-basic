import requests
from bs4 import BeautifulSoup
import os
import pandas as pd

pages = 8

result_list = []
for page in range(pages):
    # URL of the webpage you want to scrape
    url = f'https://ann.cc.ntu.edu.tw/index.asp?Page={page}&catalog='

    # add headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }

    # send a GET request to the URL
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # raise an error for bad status codes

    # parse the content of the request with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    main_table = soup.find_all('table')[4]
    titles = main_table.find_all('tr')[1:]

    # print the text from each title
    for title in titles:
        result_list.append([cell.get_text(strip=True) for cell in title.find_all('td')])
        
    print(f'\nSearching for the Page {page+1}...\n')
        
# save the result in the same directory as this program's
current_dir = os.path.dirname(os.path.abspath(__file__))
result_file_path = os.path.join(current_dir, 'ntu_announcements.xlsx')
pd.DataFrame(result_list, columns=['類別', '單位名稱', '公告主旨', '公告日期', '截止日期', '人氣']
             ).to_excel(result_file_path, index=False)

print('\nProgram Finished.\n')
