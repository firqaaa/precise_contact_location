import re
import pycountry
import locationtagger
import pycountry_convert as pc
from deep_translator import GoogleTranslator

cid_mapper = {country.name: country.alpha_2 for country in pycountry.countries}

def get_locations(locstr):
    states, cities, countries, country_id, continent_code, continent_name = None, None, None, None, None, None
    locstr = GoogleTranslator(source='auto', target='en').translate(locstr)
    place_entity = locationtagger.find_locations(text=locstr)
    ###########################################################################
    # COUNTRIES
    ###########################################################################
    if len(place_entity.countries) > 0:
        countries = place_entity.countries[0]
    else: countries = ""
    ###########################################################################
    # STATES
    ###########################################################################
    if len(place_entity.regions) > 0:
        if place_entity.cities:
            if (place_entity.regions[0] == place_entity.cities[0]) and (place_entity.regions[0] != "Central") and (place_entity.regions[0] != "Capital") and (place_entity.regions[0] != "Northern") and (place_entity.regions[0] != "Southern"):
                states = place_entity.other[0]
            elif place_entity.other:
                if (place_entity.other[0] == "Region") or (place_entity.other[0] == "Province") or (place_entity.other[0] == "Division") or (place_entity.other[0] == "District") or (place_entity.other[0] == "Capital") or (place_entity.other[0] == "District") or (place_entity.other[0] == "Governorate"):
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
                if ('Region' in i) or ('Province' in i) or ('Division' in i) or ("District" in i) or ("Capital" in i) or ("Governorate" in i):
                    try:
                        states = place_entity.regions[0]
                    except:
                        states = i
                    break
    else:
        try:
            if ("District" in place_entity.regions[0]) or ("Province" in place_entity.regions[0]):
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
    temp = []
    if len(place_entity.cities) > 0:
        cities = place_entity.cities[0]
        if (cities == "North") or (cities == "South") or (cities == "East") or (cities == "West") or (cities == "Central"):
            cities = ""
        if (cities == countries):
            for i in place_entity.other:
                if ('Region' not in i) or ('Province' not in i) or ('Division' not in i) or ('Capital' not in i) or ("District" not in i) or ("Governorate" not in i):
                    temp.append(i)
                    # cities = i
            # cities = ""
        # print(temp)
        # temp2 = []
        for j in temp:
            if (j.find("Province") != -1) or (j.find("Region") != -1) or (j.find("Division") != -1) or (j.find("Capital") != -1) or (j.find("District") != -1):
                # temp2.append(j)
                continue
            else:cities = j
        # print(temp2)
    else:
        try:
            for i in place_entity.other:
                if (i.find(countries) != -1) or (i.find("Province") != -1) or (i.find("Region") != -1) or (i.find("Division") != -1) or (i.find("Capital") != -1) or (i.find("District") != -1):
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
    ###################################################################################
    # COUNTRY CODE
    ###################################################################################
    if countries:
        country_id = cid_mapper.get(countries)
    else: country_id = ""
    ##################################################################################
    # CONTINENT / REGION CODE
    ##################################################################################
    if country_id:
        continent_code = pc.country_alpha2_to_continent_code(country_id)
    else: continent_code = ""
    ##################################################################################
    # CONTINENT / REGION NAME
    ##################################################################################
    if continent_code:
        continent_name = pc.convert_continent_code_to_continent_name(continent_code)
    else: continent_name = ""


    # states = GoogleTranslator(source="en", target=country_id.lower()).translate(states)

    return {"city": cities,
            "state": states,
            "country":countries,
            "country_code":country_id,
            "region":continent_name,
            "region_code":continent_code}

sample = "Dhaka District, Bangladesh"
loc = get_locations(sample)
print(loc)
