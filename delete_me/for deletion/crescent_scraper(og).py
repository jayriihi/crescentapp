#v3 moves from creating the image file name based on time every 5 mins on 1
# and 6 to scarping the url based on web scraping
#get current date and time subtract 15 mins and convert to string

from datetime import datetime,timedelta #for setting times
import csv #to export to csv file
import requests #to get web pages
from PIL import Image  #to manipulate image
import PIL.ImageOps #to manipulate image
import cv2 #to manipulate image
import pytesseract #to ocr read from image
import re #to use filtering numbers from string
from bs4 import BeautifulSoup #for parsing website
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import hashlib #for creating md5 hash


now_time = datetime.now() - timedelta(minutes = 0) # current date and time - 15 mins
now_time = now_time.strftime("%Y-%m-%d-%H%M") #in BWS timr format
#print (("writing_crescent_v1 {}").format(now_time))


URLC = 'http://weather.bm/tools/graphics.asp?name=CRESCENT%20GRAPH&user='
page = requests.get(URLC)
#print (type(page))
#if (type(page)) == requests.models.Response:
    #print ('page type ok')
#else:
    #print ('page type wrong')

soup = BeautifulSoup(page.content, 'html.parser')


images = soup.find(id="image")
src = images.get('src')
    #print(src)
url = ('http://weather.bm/{}').format(src)
url1 = url.replace(" ", "%20")

filename = 'windc.png'
#filename = 'windv3 {}.png'.format(now_time)
r = requests.get(url1)
open(filename, 'wb').write(r.content)

im = Image.open(filename, mode='r')
#im.show()

# Setting the points for cropped image wind speed
left = 978
top = 80
right =1140
bottom = 112

# Cropped image of above dimension 
# (It will not change orginal image) 
im1 = im.crop((left, top, right, bottom)) 
im1 = im1.save("crop_wspc.png")
cropwspc = Image.open("crop_wspc.png")
#cropwspc.show()

#convert image type
image_file = Image.open("crop_wspc.png") # open colour image
image_file = image_file.convert('L') # convert image to black and white
image_file.save('bw_crop_wspc.png')

#invert image to B&W
image = Image.open('bw_crop_wspc.png')
inverted_image = PIL.ImageOps.invert(image)
inverted_image.save('bw_crop_inv_wspc.png')
#inverted_image.show() 
#read image
img = cv2.imread('bw_crop_inv_wspc.png')
text_ws = pytesseract.image_to_string(img)

#print(text_ws)
p = re.compile(r'\d+\.\d+')  # Compile a pattern to capture float values
num_ws = [float(i) for i in p.findall(text_ws)]  # Convert strings to float
recent_ws = num_ws [0]
#print(recent_ws)



#Setting the points for cropped image max wind speed
left = 978
top = 300
right =1140
bottom = 338

# Cropped image of above dimension 
# (It will not change orginal image) 
im1 = im.crop((left, top, right, bottom)) 
im1 = im1.save("crop_mwspc.png")
cropmwspc = Image.open("crop_mwspc.png")
#cropmwspc.show()

#convert image type
image_file = Image.open("crop_mwspc.png") # open colour image
image_file = image_file.convert('L') # convert image to black and white
image_file.save('bw_crop_mwspc.png')

#invert image to B&W
image = Image.open('bw_crop_mwspc.png')
inverted_image = PIL.ImageOps.invert(image)
inverted_image.save('bw_crop_inv_mwspc.png')
#inverted_image.show() 
#read image
img = cv2.imread('bw_crop_inv_mwspc.png')
text_mws = pytesseract.image_to_string(img)

#print(text_mws)

p = re.compile(r'\d+\.\d+')  # Compile a pattern to capture float values
num_mws = [float(i) for i in p.findall(text_mws)]  # Convert strings to float
#print(num_mws)


recent_mws = num_mws[0]

#print(recent_mws)

# Setting the points for cropped image wind direction 
left = 980
top = 530
right =1140
bottom = 565

# Cropped image of above dimension 
# (It will not change orginal image) 
im1 = im.crop((left, top, right, bottom)) 

# Shows the image in image viewer 
#im1.show() 
im1 = im1.save("crop_wdc.png")

#convert image type
image_file = Image.open("crop_wdc.png") # open colour image
image_file = image_file.convert('L') # convert image to black and white
image_file.save('bw_crop_wdc.png')

#invert image to B&W
#from PIL import Image
#import PIL.ImageOps    

image = Image.open('bw_crop_wdc.png')
#image.show()

inverted_image = PIL.ImageOps.invert(image)
inverted_image.save('bw_crop_inv_wdc.png')

img = cv2.imread("bw_crop_inv_wdc.png")
text_wd = pytesseract.image_to_string(img)

#returning only floating numbers from wd string
p = re.compile(r'\d+\.\d+')  # Compile a pattern to capture float values
num_wd = [float(i) for i in p.findall(text_wd)]  # Convert strings to float
#print (num_wd)

#slice for output
recent_wd = num_wd[0]

#print(recent_wd)

    #the 'a' says to append where as a 'w' would write (from scratch)
    #for textLine in text:
    #f.write(textLine) # write data line to the open file 
    # with closes file automatically on exiting block


with open('jdatap3.csv', 'a', newline='') as file:  
    writer = csv.writer(file)
    writer.writerow([now_time,recent_ws,recent_mws,recent_wd])
    #print ("finished_writing_pearl V3")

#adding date format that GSheets can read with date/time value



now = datetime.now()- timedelta(minutes = 180)
#print("now =", now)

# dd/mm/YY H:M:S
now_time_gsheet = now.strftime("%Y/%m/%d %H:%M")
#print(now_time_gsheet)	



scope = ['https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("/Users/jriihi/Library/Mobile Documents/com~apple~CloudDocs/Documents/bermuda-weather-scraper/jays_scrapers/crescent_scraper/creds.json",scope)

client = gspread.authorize(creds)

sheet = client.open("crescent_data").sheet1

data = sheet.get_all_records()

#print (data)

data_row_add = [now_time_gsheet,recent_ws,recent_mws,recent_wd]

sheet.insert_row(data_row_add,4)

# Creating url for windguru get API
 # initializing string 
str2hash = (("{}crescent_bermudacrescentstation*").format(now_time))
#print(("{}crescent_bermudacrescentstation*").format(now_time))
# encoding Salt using encode() 
# then sending to md5() 
result = hashlib.md5(str2hash.encode()) 
  
# printing the equivalent hexadecimal value. 
#print("The hexadecimal equivalent of hash is : ", end ="") 
#print(result.hexdigest())

print(("windguru.cz/upload/api.php?uid=crescent_bermuda&salt={}&hash={}&wind_avg={}&wind_max={}&wind_direction={}").format(now_time,result.hexdigest(),recent_ws,recent_mws,recent_wd))

#send windguru pearl data via get
URL = ("http://www.windguru.cz/upload/api.php?uid=crescent_bermuda&salt={}&hash={}&wind_avg={}&wind_max={}&wind_direction={}").format(now_time,result.hexdigest(),recent_ws,recent_mws,recent_wd)
page = requests.get(URL)