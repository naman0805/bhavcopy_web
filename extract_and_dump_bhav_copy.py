import os
import requests 
from bs4 import BeautifulSoup 
import zipfile
import StringIO
import csv
import redis
from datetime import datetime
import sys
#extract


page_url = 'https://www.bseindia.com/markets/marketinfo/bhavcopy.aspx'
equity_bhav_copy_id = 'ContentPlaceHolder1_btnhylZip'
list_companies = []
headers = []
final_dict = {}
page_text = requests.get(page_url).text
soup = BeautifulSoup(page_text,'lxml')
zip_file_link = soup.find(id=equity_bhav_copy_id).get("href")

r = requests.get(zip_file_link,stream=True)
z = zipfile.ZipFile(StringIO.StringIO(r.content))
file_list = z.namelist()

if file_list:
    file_name = file_list[0] #Expecting only one file always
z.extract(file_name)
date = file_name[2:8]
r = redis.Redis(db=1)
redis_data_date = r.get('date')

if date == redis_data_date:
    sys.exit()


with open(file_name,'r') as f :
    csv_file = csv.DictReader(f)
    for line in csv_file:
        list_companies.append(line)

os.remove(file_name)
for item in list_companies:
    final_dict[item["SC_NAME"]]={"SC_NAME":item["SC_NAME"],
                                 "SC_CODE":item["SC_CODE"],
                                 "HIGH":item["HIGH"],
                                 "LOW":item["LOW"],
                                 "OPEN":item["OPEN"],
                                 "CLOSE":item["CLOSE"]}

r.flushall()
r.set('date',date)
with r.pipeline() as pipe:
    for s_name, s_details in final_dict.items():
       pipe.hmset(s_details["SC_CODE"]+':'+s_name, s_details)
       pipe.lpush("keys",s_details["SC_CODE"]+':'+s_name)
    pipe.execute()
