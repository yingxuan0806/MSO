#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 28 02:37:24 2020

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
br.open("input login page url here")

br.select_form(nr=0)
br.form['id'] = 'team name'
br.form['password'] = 'password'
br.submit()

scraped_data = {}

#3 column data
ranking_url = "url"
soup = BeautifulSoup(br.open(ranking_url), "lxml")

raw_data = soup.find_all("td")
#convert raw data to list type
raw_data = list(raw_data)

#convert list element type to string
#remove unwanted portions of the string (front and back)
for i in range(len(raw_data)):
    raw_data[i] = str(raw_data[i])
#    header row
    raw_data[i] = raw_data[i].replace("""<td align="center" bgcolor="#c8ffc8"><b>""", "")
    raw_data[i] = raw_data[i].replace("</b>\n</td>", "")
#    other teams
#    align right
    raw_data[i] = raw_data[i].replace("""<td align="right" bgcolor="c0c0c0"><font face="arial">""", "")
#    align left
    raw_data[i] = raw_data[i].replace("""<td align="left" bgcolor="c0c0c0"><font face="arial">""", "")

#    own team
    raw_data[i] = raw_data[i].replace("""<td align="right" bgcolor="#c8c8ff"><font face="arial">""", "")
    raw_data[i] = raw_data[i].replace("""<td align="left" bgcolor="#c8c8ff"><font face="arial">""", "")        
#    for all 23 teams clear back part of string
    raw_data[i] = raw_data[i].replace("""</font>\n</td>""", "")


#    remove one space character and comma of cash balance elements
#    convert to float
for i in range(5,len(raw_data), 3):
    raw_data[i] = raw_data[i].replace(" ", "")
    raw_data[i] = raw_data[i].replace(",", "")
    raw_data[i] = float(raw_data[i])
    
    
#    remove ranking numbers
#ranking_numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
for k in range(3, len(raw_data), 3):
    raw_data[k] = int(raw_data[k])

ranking_numbers = list(range(1, 24))    
for j in ranking_numbers:
    raw_data.remove(j)

    
#put data into dataframe
team_names = []
for a in range(3, len(raw_data), 2):
    team_names.append(raw_data[a])

team_cash = []
for b in range(4, len(raw_data), 2):
    team_cash.append(raw_data[b])

tuple_list = list(zip(team_names, team_cash))
    
df = pd.DataFrame(tuple_list, columns = ['Team', time.strftime("%d %b %I:%M%p")])
df["Rank"] = ranking_numbers
df.set_index("Rank", inplace = True)


#export
writer = pd.ExcelWriter('ranking.xlsx')
df.to_excel(writer, 'data')
writer.save()

#every scrape is one dataframe, then merge them into a combined data frame using join on team name
#then calculate the growth rate
#then export the excel file

#individual dataframes do not have to be exported






    
    
