
# track location and time zone using the phone number
import phonenumbers
from phonenumbers import timezone
from phonenumbers import geocoder
from phonenumbers import carrier

import folium

from opencage.geocoder import OpenCageGeocode

number = input("Enter the phone number with country code : ")
# Parsing String to the Phone number
phoneNumber = phonenumbers.parse(number)

Key = "d64186f2107c4ee0bd4c4d8c3f4df545"

# printing the timezone using the timezone module
timeZone = timezone.time_zones_for_number(phoneNumber)
print("timezone : " + str(timeZone))

# printing the geolocation of the given number using the geocoder module
geolocation = geocoder.description_for_number(phoneNumber, "en")
print("location : " + geolocation)

# printing the service provider name using the carrier module
service = carrier.name_for_number(phoneNumber, "en")
print("service provider : " + service)

# Opening OpenCage to get the latitude and longitude
geocoder = OpenCageGeocode(Key, 'http')
query = str(geolocation)
results = geocoder.geocode(query)

# Assigning the latitude and longitude
lat = results[0]['geometry']['lat']
lng = results[0]['geometry']['lng']

# Getting the map
myMap = folium.Map(location=[lat, lng], zoom_start=9)

# Adding Marker
folium.Marker([lat, lng], popup=geolocation) .add_to(myMap)

# save map to html file
myMap.save("Location.html")