from geopy.geocoders.googlev3 import GoogleV3
from geopy.geocoders import Nominatim
import xlrd


def geocode(address):
    geolocator = Nominatim(user_agent="app")
    location = geolocator.geocode(address)
    return location.raw


def reverse_geocode(lat, lon):
    geolocator = Nominatim(user_agent="app")
    location = geolocator.reverse(str(lat) + ", " + str(lon))
    return location.address


def google_geocode(address):
    geolocator = GoogleV3(api_key="AIzaSyAlhsqlHpWbBVXFPw-cAkgmD2th35LiVSQ")
    location = geolocator.geocode(address)
    return location


def google_reverse_geocode(latitude, longitude):
    geolocator = GoogleV3(api_key="AIzaSyAlhsqlHpWbBVXFPw-cAkgmD2th35LiVSQ")
    location = geolocator.reverse(str(latitude) + ", " + str(longitude))
    return location


def read_file():
    data = []
    filepath = "C:\\Users\\Bryan\\Downloads\\Cibertec_ResultadosGeo.xlsx";
    open_file = xlrd.open_workbook(filepath)
    sheet = open_file.sheet_by_name("Cibertec_ResultadosGeo")
    for i in range(sheet.nrows):
        data.append({"address": sheet.cell_value(i, 11), "latlong": sheet.cell_value(i, 12)})
    return data
