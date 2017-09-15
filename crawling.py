from bs4 import BeautifulSoup
from bs4 import re
import requests
import os
import queue as queue
import time

from mongoengine import connect
from Car import Car

if os.getenv('MONGOLAB_URI') is not None: # on Heroku
    mongolab_uri = os.getenv('MONGOLAB_URI')
    db = mongolab_uri[mongolab_uri.rfind('/')+1:] # get database name
    connect(db, host=mongolab_uri)
else:
	connect('usedCars')

def crawling(brand, model, zipcode):
	###collect all vehicle detail links, and on all pagerLinks, say 15 pages for subaru forester at 10001
	seedPage = "/used_cars/listings-sem/" + brand + "/" + model + "?zipcode=" + zipcode
	filename = brand + "_" + model + "_" + zipcode + ".csv"

	visitedPagerLinks = set()
	vehicle_detail_links = set()
	toVisitPagerLinks = queue.Queue()
	toVisitPagerLinks.put(seedPage)

	session = requests.Session()
	headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit 537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36", 
				"Accept":"text/html,application/xhtml+xml,application/xml; q=0.9,image/webp,*/*;q=0.8",
				"Accept-Encoding": "gzip, deflate, sdch",
    			"Accept-Language": "en-US,en;q=0.8",
    			"Upgrade-Insecure-Requests": "1",
    			"Cache-Control": "max-age=0",
    			"Connection": "keep-alive"}

	### on each numbered pager link, scrape all vehicle details link, and get other numbered pager links ###
	num=1
	while not toVisitPagerLinks.empty() and num <= 30:
		cur_url=toVisitPagerLinks.get()
		req = session.get("http://www.carsdirect.com" + cur_url, headers=headers)
		time.sleep(1)
		print("crawling : " + "http://www.carsdirect.com" + cur_url)
		visitedPagerLinks.add(cur_url)
		bsObj = BeautifulSoup(req.text, "html.parser")
		for link in bsObj.findAll("a"):
			if 'href' in link.attrs:
				tmp=link.attrs['href']
				if re.match(".*/vehicle-detail/.*", tmp):
					tmp2=tmp.replace("vehicle-detail", "vehicle-detail-sem")
					vehicle_detail_links.add(tmp2)

		print("now finding pagerLinks")
		for link in bsObj.findAll("a", {"class":"pagerLink"}):
			if ('href' in link.attrs) \
			and (link.attrs['href'] not in visitedPagerLinks) \
			and (re.match(".*pageNum=.*", link.attrs['href'])):
				tmp = link.attrs['href']
				toVisitPagerLinks.put(tmp)
				visitedPagerLinks.add(tmp)

		num += 1

	print("crawling detail pages...")

	for link in vehicle_detail_links:
		print("crawling " + "http://www.carsdirect.com" + link)
		time.sleep(1)

		#to deal with default 30 redirects limits, exception need to be captured
		try:
			req = session.get("http://www.carsdirect.com" + link, headers=headers)
		except requests.exceptions.TooManyRedirects as e:
			print("requests.exceptions.TooManyRedirects")
			continue

		bsObj=BeautifulSoup(req.text, "html.parser")
		
		try:
			year=bsObj.find("span", {"itemprop":"name"}).get_text().split()[0]
		except AttributeError as e:
			continue

		try:
			price=re.sub('[$, ]', '', bsObj.find("span", {"class":"price"}).get_text())
		except AttributeError as e:
			continue

		try:
			miles=re.sub('[, miles]', '', bsObj.find("span", {"class":"miles"}).get_text())
		except AttributeError as e:
			continue

		try:
			exterior=bsObj.find("div", {"class":"block-right"}).find("dl").find("dd").get_text().lower()
		except AttributeError as e:
			continue

		try:
			VIN=bsObj.find("div", {"class":"block-right"}).findAll("dl")[3].find("dd").get_text()
		except AttributeError as e:
			VIN="N/A"

		if (price == 'ContactSeller' or miles == 'ContactSeller' or exterior == 'ContactSeller'):
			continue

		Car(zipcode, brand, model, price, miles, year, exterior).save()

		print ("zipcode: " + zipcode \
				+ " brand: " + brand \
				+ " model: " + model \
				+ " price: " + str(price) \
				+ " miles: " + str(miles) \
				+ " year: " + str(year) \
				+ " exterior: " + exterior)