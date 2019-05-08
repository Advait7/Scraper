import requests
from bs4 import BeautifulSoup
import psycopg2 as p

conn = p.connect("dbname = '*********' user = '*******' password = '********' host = 'localhost'")

cur = conn.cursor()

url = "https://in.bookmyshow.com/mumbai/movies"

page = requests.get(url)

soup = BeautifulSoup(page.content, "lxml")

tag = soup.body.find_all('div', {'class':'book-button'})

links = []

for link in tag:
	try:
		links.append(link.contents[1]['href'])
	except:		
		pass

for link in links:
 	bms_link = "https://in.bookmyshow.com"
 	movie_url = "".join((bms_link, link))
	######################################
	#Each individual page scanning begins#
	######################################
	movie_page = requests.get(movie_url)

	movie_soup = BeautifulSoup(movie_page.content, "lxml")

	movie_tag = movie_soup.body.find_all('div', {'class':'sticky-filtertitle'})

	movie_name = movie_tag[0].text ##movie name
	
	#print movie_name

	movie_tag = movie_soup.body.find_all('ul', {'id':'venuelist'})

	venuelist_tag = movie_tag[0]

	venue_tag = venuelist_tag.find_all('li', {'class':'list'})

	for venue in venue_tag:
		theatre_name = venue['data-name']
		lat = venue['data-lat']
		lng = venue['data-lng']
		sub_region = venue['data-sub-region-name']
		#print theatre_name + " " + lat + " " + lng + " " + sub_region
		time_tag = venue.find_all('div', {'class':'body'})
		time_slots = time_tag[0]
		time_slots_tag = time_slots.find_all('div', {'data-online':'Y'})
		timings = ""
		prices = ""
		for time in time_slots_tag:
			temp_time = time.a['data-date-time']
			#timings.append(temp_time)
			timings = " ".join((timings, temp_time))
			temp_price = time.a['data-cat-popup']
			prices = " ".join((prices, temp_price))
			#prices.append(temp_price)
			
		if timings:	
			#print movie_name + " " + theatre_name + " " + lat + " " + lng + " " + sub_region + " " + timings + " " + prices
			cur.execute('''insert into movie(movie_name, theatre_name, lat, lng, sub_region, timings, prices) values (%s,%s,%s,%s,%s,%s,%s)''', (movie_name, theatre_name, lat, lng, sub_region, timings, prices))
			conn.commit()

cur.close()

conn.close()			