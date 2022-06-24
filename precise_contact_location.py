import re
import pycountry
import locationtagger
from rapidfuzz import fuzz
import pycountry_convert as pc
from deep_translator import GoogleTranslator
from geopy.geocoders import Nominatim

cid_mapper = {country.name: country.alpha_2 for country in pycountry.countries}

def rm_num(locstr):
    locstr = re.sub(r'\d+', '', locstr)
    return ''.join(locstr)

def get_city_state_countries_from_road(roadstr):
    geolocator = Nominatim(user_agent="geopy")
    location = geolocator.geocode(roadstr)
    addr = location.address
    addr = addr.split(',')
    country = addr[-1]
    state = addr[-3]
    city = addr[-4]
    return city, state, country

def get_country_code_and_country_using_state_only(statestr):
    try:
        geolocator = Nominatim(user_agent="geo")

        location = geolocator.geocode(statestr)
        location = geolocator.reverse("{}, {}".format(str(location.raw['lat']), str(location.raw['lon'])), exactly_one=True)

        address = location.raw['address']
        country_code = address.get('country_code', '').upper()
        country = address.get('country', '')
        return country_code, country
    except:
        pass


def get_country_code__using_city_only(citystr):
    try:
        geolocator = Nominatim(user_agent="geo")

        location = geolocator.geocode(citystr)
        location = geolocator.reverse("{}, {}".format(str(location.raw['lat']), str(location.raw['lon'])), exactly_one=True)

        address = location.raw['address']
        country_code = address.get('country_code', '').upper()
        country = address.get('country', '')
        country = GoogleTranslator(source='auto', target='en').translate(country)
        return country_code, country
    except:
        pass

def get_country_and_state_using_city_only(citystr):
    try:
        geolocator = Nominatim(user_agent="geo")

        location = geolocator.geocode(citystr)
        location = geolocator.reverse("{}, {}".format(str(location.raw['lat']), str(location.raw['lon'])), exactly_one=True)

        address = location.raw['address']
        state = address.get('state', '')
        country = address.get('country', '')
        return state, country
    except:
        pass

def get_locations(locstr):
    states, cities, countries, country_id, continent_code, continent_name = None, None, None, None, None, None
    locstr = locstr.title()
    ############################################################################
    # ROAD
    ############################################################################
    if (type(locstr.split(' ')[0]) == int)\
            or (locstr.split(' ')[-1] == "Road")\
            or (locstr.split(' ')[-1] == "ROAD"):
        try:
            cities, states, countries = get_city_state_countries_from_road(locstr)
            cities = cities.strip()
            states = states.strip()
            countries = countries.strip()
        except:
            # remove street number
            locstr = rm_num(locstr)
            if len(locstr.split(',')) > 3:
                # only pick state, country
                locstr = ",".join(locstr.split(',')[-2:])

    place_entity = locationtagger.find_locations(text=locstr)
    ###########################################################################
    # COUNTRIES
    ###########################################################################
    if countries == None:
        if len(place_entity.countries) > 0:
            countries = place_entity.countries[0]
        else: countries = ""
    ###########################################################################
    # STATES
    ###########################################################################
    if states == None:
        if len(place_entity.regions) > 0:
            if place_entity.cities:
                if (place_entity.regions[0] == place_entity.cities[0])\
                        and (place_entity.regions[0] != "Central")\
                        and (place_entity.regions[0] != "Capital")\
                        and (place_entity.regions[0] != "Northern")\
                        and (place_entity.regions[0] != "Southern")\
                        and (place_entity.regions[0] != "Eastern")\
                        and (place_entity.regions[0] != "Western")\
                        and (place_entity.regions[0] != "North")\
                        and (place_entity.regions[0] != "South")\
                        and (place_entity.regions[0] != "East")\
                        and (place_entity.regions[0] != "West"):
                    if place_entity.other:
                        states = place_entity.other[0]
                elif place_entity.other:
                    if (place_entity.other[0] == "Region")\
                            or (place_entity.other[0] == "Province")\
                            or (place_entity.other[0] == "Division")\
                            or (place_entity.other[0] == "District")\
                            or (place_entity.other[0] == "Capital")\
                            or (place_entity.other[0] == "Governorate")\
                            or (place_entity.other[0] == "Coast"):
                        if (place_entity.regions[0].find(place_entity.other[0]) == -1):
                            states = place_entity.regions[0] + ' ' + place_entity.other[0]
                        else:
                            states = place_entity.regions[0]
                else:
                    states = place_entity.regions[0]
            else:
                states = place_entity.regions[0]
        elif len(place_entity.other) > 0:
            states = place_entity.other[0]
            try:
                if states in place_entity.cities[0]:
                    states = place_entity.cities[0]
                else:states = place_entity.regions[0]
            except:
                for i in place_entity.other:
                    if ('Region' in i)\
                            or ('Province' in i)\
                            or ('Division' in i)\
                            or ("District" in i)\
                            or ("Capital" in i)\
                            or ("Governorate" in i)\
                            or ("Coast" in i):
                        try:
                            states = place_entity.regions[0]
                        except:
                            states = i
                        break
        else:
            try:
                if ("District" in place_entity.regions[0])\
                        or ("Province" in place_entity.regions[0])\
                        or ("Coast" in place_entity.regions[0]):
                    states = place_entity.regions[0]
            except:
                states = ""

        if states == None:
            if place_entity.regions:
                states = place_entity.regions[0]
        if states == "Surrounding Area":
            states = ""
    #########################################################################
    # CITIES
    #########################################################################
    if cities == None:
        temp = []
        if len(place_entity.cities) > 0:
            cities = place_entity.cities[0]
            if (cities == "North")\
                    or (cities == "South")\
                    or (cities == "East")\
                    or (cities == "West")\
                    or (cities == "Central"):
                cities = ""
            if (cities == countries):
                for i in place_entity.other:
                    if ('Region' not in i)\
                            or ('Province' not in i)\
                            or ('Division' not in i)\
                            or ('Capital' not in i)\
                            or ("District" not in i)\
                            or ("Governorate" not in i)\
                            or ("Coast" not in i):
                        temp.append(i)
                        # cities = i
                # cities = ""
            # print(temp)
            # temp2 = []
            for j in temp:
                if (j.find("Province") != -1)\
                        or (j.find("Region") != -1)\
                        or (j.find("Division") != -1)\
                        or (j.find("Capital") != -1)\
                        or (j.find("District") != -1)\
                        or (j.find("Coast") != -1):
                    # temp2.append(j)
                    continue
                else:cities = j
            # print(temp2)
        else:
            try:
                for i in place_entity.other:
                    if (i.find(countries) != -1)\
                            or (i.find("Province") != -1)\
                            or (i.find("Region") != -1)\
                            or (i.find("Division") != -1)\
                            or (i.find("Capital") != -1)\
                            or (i.find("District") != -1)\
                            or (i.find("Coast") != -1):
                        continue
                    else:
                        cities = i
            except:
                cities = ""

        if cities == "Prefecture":
            cities = ""
            states = states + " " + "Prefecture"

        if (cities == states) or (cities == countries) or (cities == None):
            cities = ""

        try:
            if (cities != '') and (states == '') and (countries == ''):
                country_id, countries = get_country_code__using_city_only(cities)
        except:
            country_id, countries = "", ""

        try:
            if (len(states) == 2) or (len(states) == 3):
                states, countries = get_country_and_state_using_city_only(locstr)
        except:
            states, countries = "", ""


        if (locstr.split(" ")[0] == "Greater") or (locstr.split(" ")[-1] == "Area") :
            states = locstr
            locstr = ' '.join(locstr.split(' ')[1:])
            geolocator = Nominatim(user_agent="geo")
            location = geolocator.geocode(locstr)
            try:
                location = geolocator.reverse("{}, {}".format(str(location.raw['lat']), str(location.raw['lon'])), exactly_one=True)
                address = location.raw['address']
                cities = address.get('city', '').strip()
                countries = address.get('country', '').strip()
            except:
                cities = ""
                countries = ""
    ###################################################################################
    # COUNTRY CODE
    ###################################################################################
    if countries:
        country_id = cid_mapper.get(countries.strip())
    else: country_id = ""

    try:
        if (country_id == '') and (states != ''):
            country_id, countries = get_country_code_and_country_using_state_only(states.strip())
    except:
        country_id, countries = "", ""
    ##################################################################################
    # CONTINENT / REGION CODE
    ##################################################################################
    if country_id:
        continent_code = pc.country_alpha2_to_continent_code(country_id.strip())
    else: continent_code = ""
    ##################################################################################
    # CONTINENT / REGION NAME
    ##################################################################################
    if continent_code:
        continent_name = pc.convert_continent_code_to_continent_name(continent_code.strip())
    else: continent_name = ""

    ##################################################################################
    # STATE BACK-TRANSLATION
    ##################################################################################
    # states = GoogleTranslator(source="en", target=country_id.lower()).translate(states)

    if fuzz.ratio(states, countries) > 50.:
        states = ""

    return {"city": cities,
            "state": states,
            "country":countries,
            "country_code":country_id,
            "region":continent_name,
            "region_code":continent_code}

sample = "57 PIONEER ROAD"
loc = get_locations(sample)
print(loc)
