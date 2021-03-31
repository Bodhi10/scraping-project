import pandas
import requests
from bs4 import BeautifulSoup
import argparse
import connect

parser = argparse.ArgumentParser()
parser.add_argument("--pg_num_max", help = "Enter the number of page  to parse", type = int)
parser.add_argument("--dbname", help = "Enter the name of db", type = str)
args = parser.parse_args()

oyo_url = "https://www.oyorooms.com/hotels-in-kolkata//?page="
hdr = {'User-Agent': 'Mozilla/5.0'}
scraped_info_list = []
pg_num_max = args.pg_num_max
connect.connect(args.dbname)

for pg_num in range(1, pg_num_max):
    print("GET request for " + str(oyo_url)+str(pg_num))
    req = requests.get(oyo_url+str(pg_num), headers=hdr)
    content = req.content

    soup = BeautifulSoup(content, "html.parser")
    all_hotels = soup.find_all("div", {"class": "hotelCardListing"})


    for hotel in all_hotels:
        hotel_info = {}
        hotel_info["Name"] = hotel.find("h3", {"class": "listingHotelDescription__hotelName"}).text
        hotel_info["Address"] = hotel.find("span", {"itemprop": "streetAddress"}).text
        try:
            hotel_info["Rating"] = hotel.find("span", {"class": "hotelRating__ratingSummary"}).text
        except AttributeError:
            hotel_info["Rating"] = None

        hotel_info["Price"] = hotel.find("span", {"class": "listingPrice__finalPrice"}).text
        parent_amenities_element = hotel.find("div", {"class": "amenityWrapper"})
        amenities_list = []
        for amenity in parent_amenities_element.find_all("div", {"class": "amenityWrapper__amenity"}):
            amenities_list.append(amenity.find("span", {"class": "d-body-sm"}).text.strip())

        hotel_info["Amenities"] = ', '.join(amenities_list[:-1])
        scraped_info_list.append(hotel_info)
        connect.insert_into_table(args.dbname, tuple(hotel_info.values()))


#print(scraped_info_list)
dataFrame = pandas.DataFrame(scraped_info_list)
print("Creating csv file...")
dataFrame.to_csv("oyo.csv")
connect.get_hotel_info(args.dbname)
