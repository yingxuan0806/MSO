#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 17:33:05 2020

@author: yingxuan
"""

import time
import mechanize
from bs4 import BeautifulSoup
import http.cookiejar as cookielib
import pandas as pd
import numpy as np


cj = cookielib.CookieJar()
br = mechanize.Browser()

#ignore robots.txt
br.set_handle_robots(False)
br.set_handle_equiv(False)

br.set_cookiejar(cj)
br.open("login page url")

br.select_form(nr=0)
br.form['id'] = 'group name'
br.form['password'] = 'password'
br.submit()

url_list = ["CASH", "JOBIN", "JOBQ", "S1Q", "S2Q", "S3Q", "S1UTIL", "S2UTIL", "S3UTIL"]


#url_list = ["Cash", "Accepted_Jobs", "Queued_Jobs","S1_Queue", "S1_Utilisation",\
#            "S2_Queue", "S2_Utilisation", "S3_Queue", "S3_Utilisation"]

#url_list_4col = ["Job_T", "Revenue", "Completed Jobs"]

#JOBT = lead time
#JOBREV = revenue
#JOBOUT = completed jobs

url_list_4col = ["JOBT", "JOBREV", "JOBOUT"]

scraped_data = {}



#base case test before placing a loop to scrape all two column tables
#get inventory
inventory_url = "url"
soup = BeautifulSoup(br.open(inventory_url), "lxml")
data = soup.find_all("script")[5].string
data = data.split("\n")[4].split("'")[3].split()
counter = 1

for i in data:
    if counter % 2 == 1:
        counter += 1
        day = float(i)
        scraped_data[day] = []
    elif counter % 2 == 0:
        row_data = [float(i)]
        scraped_data[day].extend(row_data)
        counter += 1
        

#iterate and scrape all two-column tabl"es
for url in url_list:
#    either line works
#    lf_url = "http://op.responsive.net/Littlefield/Plot?data=%s&x=all" % url
    lf_url = "http://op.responsive.net/Littlefield/Plot?data={}&x=all".format(url)
    print(lf_url)
    soup = BeautifulSoup(br.open(lf_url), "lxml")
    data = soup.find_all("script")[5].string
    data = data.split("\n")[4].split("'")[3].split()
    counter = 1
    for i in data:
        if counter % 2 == 0:
            day = counter / 2
            scraped_data[day].append(float(i))
            counter += 1
        else:
            counter += 1

print("2 column data scraped.")


#iterate and scrape all four-column tables
for url in url_list_4col:
    lf_url = "http://op.responsive.net/Littlefield/Plot?data={}&x=all".format(url)
    soup = BeautifulSoup(br.open(lf_url), "lxml")
    data = soup.find_all("script")[5].string
    data0 = data.split("\n")[4].split("'")[5].split()
    data1 = data.split("\n")[5].split("'")[5].split()
    data2 = data.split("\n")[6].split("'")[5].split()
    
    counter = 1
    for i in data0:
        if counter % 2 == 0:
            day = counter / 2
            scraped_data[day].append(float(i))
            counter += 1
        else:
            counter += 1

    counter = 1
    for i in data1:
        if counter % 2 == 0:
            day = counter / 2
            scraped_data[day].append(float(i))
            counter += 1
        else:
            counter += 1

    counter = 1
    for i in data2:
        if counter % 2 == 0:
            day = counter / 2
            scraped_data[day].append(float(i))
            counter += 1
        else:
            counter += 1
    
print("4 column data scraped.")

#Add dummy data to fill out fractional day rows
dummy_data = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
#dummy_data = [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan,]
for key, value in scraped_data.items():
    if len(value) < 19:
        value.extend(dummy_data)
        
print("dummy data added")        
        
#headers = []

#JOB 1/2/3 refers to contract number
headers = ["INV","CASH","JOBIN","JOBQ","S1Q","S2Q","S3Q","S1UTIL","S2UTIL","S3UTIL",\
           "JOBT1","JOBT2","JOBT3","JOBREV1","JOBREV2","JOBREV3",\
           "JOBOUT1","JOBOUT2","JOBOUT3"]

df = pd.DataFrame.from_dict(scraped_data, orient="index")
df.columns = headers
df.sort_index(inplace = True)

df["Backlog"] = df["JOBIN"].cumsum() - df["JOBOUT1"].cumsum() - df["JOBOUT2"].cumsum() - df["JOBOUT3"].cumsum()

#rename scraped column headers
df = df.rename(columns = {"INV": "Inventory", "CASH": "Cash", "JOBIN": "Accepted Jobs", "JOBQ": "Queued Jobs", \
                     "S1Q": "S1 Queue", "S2Q": "S2 Queue", "S3Q": "S3 Queue", \
                     "S1UTIL": "S1 Util", "S2UTIL": "S2 Util", "S3UTIL": "S3 Util", \
                     "JOBT1": "Contract 1 Lead-time", "JOBT2": "Contract 2 Lead-time", "JOBT3": "Contract 3 Lead-time", \
                     "JOBREV1":"Contract 1 Revenue", "JOBREV2": "Contract 2 Revenue", "JOBREV3": "Contract 3 Revenue", \
                     "JOBOUT1": "Contract 1 Completed", "JOBOUT2": "Contract 2 Completed", "JOBOUT3": "Contract 3 Completed"})


#REMOVE FRACTIONAL ROWS
#first, obtain a list of index names that are fractional
index_names = df[df["Cash"] == 0.0].index
#then, remove the rows that are of fractional index labels
df.drop(index_names, inplace = True)
print("Fractional columns dropped")


#COLUMNS TO ADD
#inventory used
#df["Inv Used"] = 0
df["Inv Used"] = df["Inventory"]
for count in range(len(df)):
    df["Inv Used"].values[count] = df["Inventory"].values[count-1] - df["Inventory"].values[count]
    if df["Inv Used"].values[count] < 0:
        df["Inv Used"].values[count] = np.nan
    else:
        continue

#assignment description: started with 9600 inventory kits on day 1
df["Inv Used"].values[0] = 9600 - df["Inventory"].values[0]


#total revenue growth
df["Revenue Growth ($k)"] = df["Cash"]
for count1 in range(len(df)):
    df["Revenue Growth ($k)"].values[count1] = df["Cash"].values[count1] - df["Cash"].values[count1-1]
    if df["Revenue Growth ($k)"].values[count1] < 0:
        df["Revenue Growth ($k)"].values[count1] = np.nan
    else:
        continue

#assign NaN growth on day 1
df["Revenue Growth ($k)"].values[0] = np.nan


#revenue growth rate
df["Revenue Growth (%)"] = float(0)
for count2 in range(len(df)):
    df["Revenue Growth (%)"].values[count2] = df["Revenue Growth ($k)"].values[count2] / df["Cash"].values[count2-1]
#    removing outlier values (eg. more than 100% growth rate -> due to purchasing inventory so cash on hand went down exponentially)
    if df["Revenue Growth (%)"].values[count2] < 0 or df["Revenue Growth (%)"].values[count2] > 1:
        df["Revenue Growth (%)"].values[count2] = np.nan
    else: continue
    
    
#    if df["Revenue Growth (%)"].values[count2] == np.inf:
#        df["Revenue Growth (%)"].values[count2] = df["Revenue Growth (%)"].values[count2].replace(np.inf, np.nan)
#    else:
#        continue
    
#    if count2 != 0:
#        df["Revenue Growth (%)"].values[count2] = df["Revenue Growth ($k)"].values[count2] / df["Cash"].values[count2-1]
#        if df["Revenue Growth (%)"].values[count2] == np.inf:
#            df["Revenue Growth (%)"].values[count2] = df["Revenue Growth (%)"].values[count2].replace(np.inf, np.nan)
#        else:
#            continue
#    else:
#        df["Revenue Growth (%)"].values[count2] = np.nan
        
        
#COLUMNS TO EDIT
#purpose: to remove all the null zero values in the calculation of mean, stdev and median.
#set the values as NaN to skip all NaN values in the calculations.

#Contract 1 Lead-time
for a in range(len(df)):
    if df["Contract 1 Lead-time"].values[a] == 0:
        df["Contract 1 Lead-time"].values[a] = np.nan
    else:
        continue
    
#Contract 2 Lead-time    
for b in range(len(df)):
    if df["Contract 2 Lead-time"].values[b] == 0:
        df["Contract 2 Lead-time"].values[b] = np.nan
    else:
        continue
    
#Contract 3 Lead-time    
for c in range(len(df)):
    if df["Contract 3 Lead-time"].values[c] == 0:
        df["Contract 3 Lead-time"].values[c] = np.nan
    else:
        continue


#Contract 1 Revenue
for d in range(len(df)):
    if df["Contract 1 Revenue"].values[d] == 0:
        df["Contract 1 Revenue"].values[d] = np.nan
    else:
        continue

#Contract 2 Revenue
for e in range(len(df)):
    if df["Contract 2 Revenue"].values[e] == 0:
        df["Contract 2 Revenue"].values[e] = np.nan
    else:
        continue

#Contract 3 Revenue
for f in range(len(df)):
    if df["Contract 3 Revenue"].values[f] == 0:
        df["Contract 3 Revenue"].values[f] = np.nan
    else:
        continue
         
#Contract 1 Completed
for g in range(len(df)):
    if df["Contract 1 Completed"].values[g] == 0:
        df["Contract 1 Completed"].values[g] = np.nan
    else:
        continue
    
#Contract 2 Completed
for h in range(len(df)):
    if df["Contract 2 Completed"].values[h] == 0:
        df["Contract 2 Completed"].values[h] = np.nan
    else:
        continue

#Contract 3 Completed
for k in range(len(df)):
    if df["Contract 3 Completed"].values[k] == 0:
        df["Contract 3 Completed"].values[k] = np.nan
    else:
        continue
        
        
#ROWS TO ADD
#average
mean = df.mean(axis = 0, skipna = True)
df = df.append(mean, ignore_index = True)


#standard deviation
stdev = df.std(axis = 0, skipna = True)
df = df.append(stdev, ignore_index = True)


#median
median = df.median(axis = 0, skipna = True)
df = df.append(median, ignore_index = True)


#set day number as dataframe index
total_days = len(df) - 3
days_list = list(range(1, total_days + 1))
days_list.append("Mean")
days_list.append("Deviation")
days_list.append("Median")
df["Day"] = days_list
df.set_index("Day", inplace = True)
#df = df.rename(index={df.index[-3]:"Mean"})
#df = df.rename(index={df.index[-2]:"Deviation"})
#df = df.rename(index={df.index[-1]:"Median"})
    
#rearrange column sequence
df = df[["Inventory", "Inv Used", "Cash", "Accepted Jobs", "Backlog", \
         "Contract 3 Lead-time", "Contract 3 Revenue", \
         "S1 Queue", "S1 Util", "S2 Queue", "S2 Util", "S3 Queue", "S3 Util",\
         "Revenue Growth ($k)", "Revenue Growth (%)", "Queued Jobs", \
         "Contract 3 Completed", "Contract 2 Completed", "Contract 1 Completed", \
         "Contract 1 Lead-time", "Contract 1 Revenue", "Contract 2 Lead-time", "Contract 2 Revenue"]]    
    
#fix column width for easier viewing



#print(df)

print("exporting")

#export full data
writer = pd.ExcelWriter('fulldata.xlsx')
df.to_excel(writer, 'data')
writer.save()


#data for only latest 10 days for easy viewing no need scroll
df_less = df.copy()
df_less = df.iloc[-13:]
#print(df_less)
writer_last_10_days = pd.ExcelWriter('final10data.xlsx')
df_less.to_excel(writer_last_10_days, 'data')
writer_last_10_days.save()


print("\nGMT: "+time.strftime("%a, %d %b %Y %I:%M:%S %p %Z", time.gmtime()))
print("Local: "+time.strftime("%a, %d %b %Y %I:%M:%S %p %Z\n"))





