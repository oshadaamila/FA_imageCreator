# -*- coding: utf-8 -*-
"""
Created on Tue May 31 21:10:47 2022

@author: oshadaa
"""

import pdfplumber
import requests 
from bs4 import BeautifulSoup
from os.path import exists
import sys
import os
from glob import glob
from PIL import Image, ImageFont, ImageDraw
from tkinter import messagebox

def find_indicator_position(water_level):
    if( water_level > 8.5) :
        return 410
    elif (water_level < 1.0):
        return 1060
    else:
        return 1200 - ((785/9)*water_level + 33)

def find_slider_position(water_level):
    if (water_level > 6.5) :
        return 410
    elif (water_level < 3.0):
        return 800
    else:
        return find_indicator_position(water_level) - 160

def find_alert_position(water_level):
    if (water_level < 3.0):
        return (48,1098)
    else:
        return (630, int(find_slider_position(water_level) + 350))
    
def formatTime(time):
    if time == "12:00 MID NIGHT":
        return "12:00AM"
    elif time == "12:00 NOON":
        return "12:00PM"
    else:
        return time

def getAlertColor(alert):
    if alert == "ALERT":
        return (255,242,0)
    elif alert == "NORMAL":
        return (0,255,0)
    else:
        return (0,0,0)


# TODO implement

r = requests.get('http://www.dmc.gov.lk/index.php?option=com_dmcreports&view=reports&Itemid=277&search=Water%20Level&report_type_id=6&todate=&fromdate=&lang=en')

# Parsing the HTML
soup = BeautifulSoup(r.content, 'html.parser')

# Finding by id
s = soup.find('td', class_= 'sandplustd')
row_el = soup.find('tr', class_ = 'rowdate_0')
date_el = row_el.select_one(":nth-child(2)")
report_date = date_el.text

linkel = s.find('a')
pdfSource = 'http://www.dmc.gov.lk' + linkel.get('href')
latestFileName = linkel.get('href').split('/')[3]

if (exists(latestFileName)):
    print("latest File already exists!")
    messagebox.showerror(title="Image Creator - Error", message="latest File already exists!")
    sys.exit(0)

for file in glob('Water_Level*.pdf'):
    os.remove(file)
    
r = requests.get(pdfSource, allow_redirects=True)

open(latestFileName, 'wb').write(r.content)

message = ""
secondTime = ""
with pdfplumber.open(latestFileName) as pdf:
    first_page = pdf.pages[0]
    #string = ""
    #for x in first_page.chars:
        #string += (x['text'])
    #print (string)
    table = first_page.extract_table(table_settings={})
    firstTime = str(table[0][9]).replace('\n', '')
    secondTime = str(table[0][10]).replace('\n', '')
    firstWaterLevel = str(table[2][9])
    secondWaterLevel = str(table[2][10])
    waterLevelStatus = str(table[2][11])
    message = "Flood Alert- Nagalagam Weediya \n" + firstTime + ": " + firstWaterLevel + "m\n" +secondTime + ": " + secondWaterLevel + "m\n" + "Water Level: " + waterLevelStatus


#create Slider
slider = Image.open("resources/template1.png")
image_editable = ImageDraw.Draw(slider)
image_editable.text((74,40), report_date, (0, 0, 0), font=ImageFont.truetype('resources/Roboto-Bold.ttf', 63))
image_editable.text((70,100), formatTime(secondTime[15:len(secondTime)].upper()), (0, 0, 0), font=ImageFont.truetype('resources/Roboto-Bold.ttf', 40))
image_editable.text((74,175), secondWaterLevel + " ft", (0, 0, 0), font=ImageFont.truetype('resources/Roboto-Regular.ttf', 110))
slider.save("slider.png")

indicator = Image.open("resources/indicator.png")
slider_2 = Image.open("slider.png")
background = Image.open("resources/template2.png")
indicator_pos = find_indicator_position(float(secondWaterLevel))
slider_pos = find_slider_position(float(secondWaterLevel))

background.paste(indicator, (500,int(indicator_pos)), indicator)
background.paste(slider_2,(559,int(slider_pos)))

sinhalaTxt = "kd.,.xùÈh "
image_edit = ImageDraw.Draw(background)
image_edit.text((630,int(slider_pos) - 80), sinhalaTxt, (0, 0, 0), font=ImageFont.truetype('resources/0KDSAMAN Regular.ttf', 70))
image_edit.text(find_alert_position(float(secondWaterLevel)), waterLevelStatus.upper(), getAlertColor(waterLevelStatus.upper()),ImageFont.truetype('resources/Roboto-Bold.ttf', 80))
background.save("finalImage.png")


messagebox.showinfo(title="Image Creator - Success", message="Image Created finalImage.jpg!")
background.show()
print (message)
