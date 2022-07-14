import re
import spacy
import string
import pycountry
import locationtagger
import spacy_fastlang
import translators as ts
from rapidfuzz import fuzz
import pycountry_convert as pc
from deep_translator import GoogleTranslator
from geopy.geocoders import Nominatim

from multiprocessing.pool import ThreadPool as Pool
from functools import lru_cache
import warnings
warnings.filterwarnings('ignore')

@lru_cache(maxsize=128)
def detect_language(text):
    nlp = spacy.blank("xx")
    nlp.add_pipe("language_detector")
    doc = nlp(text)
    return doc._.language

# def translate_to_english(text):
#     return ts.google(text)

cid_mapper = {country.name: country.alpha_2 for country in pycountry.countries}

@lru_cache(maxsize=128)
def rm_num(locstr):
    locstr = re.sub(r'\d+', '', locstr)
    return ''.join(locstr)

@lru_cache(maxsize=128)
def preproc(locstr):
  pattern = re.compile("Town|City|Head|Building|Office|City|Of|And|Transportation|STE|D.C|Metro|Tn.", flags=re.I)
  return pattern.sub("", locstr).strip()

@lru_cache(maxsize=128)
def detect_backslash(pass_string): 
  regex= re.compile('[/]') 
  if(regex.search(pass_string) != None):
    sub_string = pass_string.split('/')[1].strip()
    if len(pass_string.split(',')) == 2:
      return sub_string + "," + pass_string.split(',')[-1]
    elif len(pass_string.split(',')) == 3:
      return sub_string + "," + " ".join(pass_string.split(',')[-2:])
    else:
      return sub_string
  else: 
      return pass_string

@lru_cache(maxsize=128)
def detect_dash(pass_string): 
  regex= re.compile('[-]') 
  if(regex.search(pass_string) != None):
    sub_string = pass_string.split('-')[1].strip()
    if len(pass_string.split(',')) == 2:
      return sub_string
    elif len(pass_string.split(',')) == 3:
      return sub_string
    else:
      return sub_string
  else: 
      return pass_string

@lru_cache(maxsize=128)
def detect_pipe(pass_string): 
  regex= re.compile('[|]') 
  if(regex.search(pass_string) != None):
    sub_string = pass_string.split('|')[1].strip()
    if len(pass_string.split(',')) == 2:
      return sub_string + "," + pass_string.split(',')[-1]
    elif len(pass_string.split(',')) == 3:
      return sub_string + "," + ' '.join(pass_string.split(',')[-2:])
    else:
      return sub_string
  else: 
      return pass_string

@lru_cache(maxsize=128)
def detect_and1(pass_string): 
  regex= re.compile('[&]') 
  if(regex.search(pass_string) != None):
    sub_string = pass_string.split('&')[1].strip()
    if len(pass_string.split(',')) == 2:
      return sub_string + "," + pass_string.split(',')[-1]
    elif len(pass_string.split(',')) == 3:
      return sub_string + "," + ' '.join(pass_string.split(',')[-2:])
    else:
      return sub_string
  else: 
      return pass_string

@lru_cache(maxsize=128)
def get_state_country(citystr):
  try:
    geolocator = Nominatim(user_agent="geopy1", timeout=3)
    location = geolocator.geocode(citystr)
    location = geolocator.reverse("{}, {}".format(str(location.raw['lat']), str(location.raw['lon'])), exactly_one=True)
    address = location.raw['address']
    state = address.get('state', None)
    country = address.get('country', None)
    return state, country
  except:
    pass

@lru_cache(maxsize=128)
def get_city_state_countries_from_road(roadstr):
  try:
      geolocator = Nominatim(user_agent="geopy2", timeout=3)
      location = geolocator.geocode(roadstr)
      addr = location.address
      addr = addr.split(',')
      country = addr[-1]
      state = addr[-3]
      city = addr[-4]
      return city, state, country
  except:
    pass

@lru_cache(maxsize=128)
def get_country_code_and_country_using_state_only(statestr):
    try:
        geolocator = Nominatim(user_agent="geopy3",timeout=3)

        location = geolocator.geocode(statestr)
        location = geolocator.reverse("{}, {}".format(str(location.raw['lat']), str(location.raw['lon'])), exactly_one=True)

        address = location.raw['address']
        country_code = address.get('country_code', '').upper()
        country = address.get('country', '')
        return country_code, country
    except:
        pass

@lru_cache(maxsize=128)
def get_country_code__using_city_only(citystr):
    try:
        geolocator = Nominatim(user_agent="geopy4", timeout=3)

        location = geolocator.geocode(citystr)
        location = geolocator.reverse("{}, {}".format(str(location.raw['lat']), str(location.raw['lon'])), exactly_one=True)

        address = location.raw['address']
        country_code = address.get('country_code', '').upper()
        country = address.get('country', '')
        country = GoogleTranslator(source='auto', target='en').translate(country)
        return country_code, country
    except:
        pass

@lru_cache(maxsize=128)
def get_country_and_state_using_city_only(citystr):
    try:
        geolocator = Nominatim(user_agent="geopy5", timeout=3)

        location = geolocator.geocode(citystr)
        location = geolocator.reverse("{}, {}".format(str(location.raw['lat']), str(location.raw['lon'])), exactly_one=True)

        address = location.raw['address']
        state = address.get('state', '')
        country = address.get('country', '')
        return state, country
    except:
        pass

@lru_cache(maxsize=128)
def get_countries_using_states_only(statestr):
    try:
        geolocator = Nominatim(user_agent="geopy15", timeout=3)

        location = geolocator.geocode(statestr)
        location = geolocator.reverse("{}, {}".format(str(location.raw['lat']), str(location.raw['lon'])), exactly_one=True)

        address = location.raw['address']
        country = address.get('country', '')
        return country
    except:
        pass

@lru_cache(maxsize=128)
def get_all_the_things(locstr):
    try:
        geolocator = Nominatim(user_agent="geopy25", timeout=3)

        location = geolocator.geocode(locstr)
        location = geolocator.reverse("{}, {}".format(str(location.raw['lat']), str(location.raw['lon'])), exactly_one=True)

        address = location.raw['address']
        city = address.get('city', '')
        state = address.get('state', '')
        country = address.get('country', '')
        return city, state, country
    except:
        pass

@lru_cache(maxsize=128)
def get_country_code_using_only_country(countrystr):
  try:
    geolocator = Nominatim(user_agent="geo32", timeout=3)
    location = geolocator.geocode(countrystr)
    location = geolocator.reverse("{}, {}".format(str(location.raw['lat']), str(location.raw['lon'])), exactly_one=True)
    address = location.raw['address']
    country_code = address.get('country_code', '').upper()
    return country_code
  except:
    pass

@lru_cache(maxsize=128)
def get_locations(locstr):
  
  if (locstr == None) or (locstr == ""):
    return {
        "city":"",
        "state":"",
        "country":"",
        "country_code": "",
        "region":"",
        "region_code":""}
          
  states, cities, countries, country_id, continent_code, continent_name = None, None, None, None, None, None

  if locstr.isupper():
    locstr = locstr.title()
  locstr = preproc(locstr)
  ############################################################################
  # ROAD REFORMATING (ex: 159, Sin Ming Road # 07-02 Lobby 2 Amtech Building
  # --> 159, Sin Ming Road)
  ############################################################################
  road_set = {"Road", "ROAD", "road", "Street", "street"}
  try: 
    road = [ele for ele in locstr.split(" ") if ele in road_set][0]
  except:
    road = None
  try:
    if road:
      locstr = locstr[0:re.search(r"{}".format(road), locstr, flags=re.IGNORECASE).end()]
  except:
    pass
  ############################################################################
  ### PREPROCESSING
  ############################################################################
  locstr = detect_pipe(locstr)
  # locstr = detect_and1(locstr)
  locstr = detect_dash(locstr)
  locstr = detect_backslash(locstr)
  
  if len(locstr.split(" ")[0]) == 1:
    locstr = locstr[2:]
  ############################################################################
  # ROAD 
  ############################################################################
  if re.findall('[0-9]+', locstr) or road:
      try:
          cities, states, countries = get_city_state_countries_from_road(locstr)
          cities = cities.strip()
          states = states.strip()
          countries = countries.strip()
      except:
        pass
  ###########################################################################

  ###########################################################################
  # COUNTRY ONLY
  ###########################################################################
  if locstr.title() in set(countriesList):
      countries = locstr
  ############################################################################

  ###########################################################################
  # CITY ONLY
  ###########################################################################
  if locstr in set(citiesList):
    cities = locstr
    try:
      states, countries = get_country_and_state_using_city_only(locstr)
    except:
      states = ""
      countries = ""
  ############################################################################
  
  ###########################################################################
  # STATES ONLY
  ###########################################################################
  if locstr in set(statesList):
    states = locstr
    countries = get_countries_using_states_only(locstr)
  ############################################################################
  ############################################################################
  # CITY - STATES
  ############################################################################
  loc_split_by_comma = locstr.split(",")
  if (len(loc_split_by_comma) == 2) and (len(loc_split_by_comma[-1].strip()) > 2):
    if loc_split_by_comma[0] in set(citiesList):
      cities = loc_split_by_comma[0]
    if loc_split_by_comma[-1].strip() in set(statesList):
      states = loc_split_by_comma[-1].strip()
    try:
      locstr = cities + ", " + states
    except:
      pass
  
  ############################################################################

  ############################################################################
  ## THIS CODE TO SOLVE CITY - STATE CODE FORMAT (ex: Bonney Lake, WA) #######
  ############################################################################ 
  if (len(loc_split_by_comma) == 2):
    if len(loc_split_by_comma[-1].strip()):
      if statesCodeToStatesName.get(loc_split_by_comma[-1].strip()) and len(statesCodeToStatesName.get(loc_split_by_comma[-1].strip())) > 1:
        if loc_split_by_comma[0] in set(citiesList):
          cities = loc_split_by_comma[0]
          try:
            states, countries = get_state_country(locstr)
          except:
            states, countries = "", ""
          if type(states) == list:
            states = states[0]
      elif statesCodeToStatesName.get(loc_split_by_comma[-1].strip()) and len(statesCodeToStatesName.get(loc_split_by_comma[-1].strip())) == 1:
        cities = loc_split_by_comma[0]
        states = statesCodeToStatesName.get(loc_split_by_comma[-1].strip())
        if type(states) == list:
          states = states[0]
  else:
    locstr = locstr
  ############################################################################

  ############################################################################
  ## THIS CODE TO SOLVE CITY - STATE AREA OR STATE AREA FORMAT 
  ## (ex: Greater Jakarta Area / Richland, Washington Area)
  ############################################################################
  loc_split_by_space = locstr.split(" ")
  if (loc_split_by_space[0] == "Greater") and (loc_split_by_space[-1] == "Area"):
    locstr = ' '.join(loc_split_by_space[1:-1]).strip()
    geolocator = Nominatim(user_agent="geo11", timeout=3)
    location = geolocator.geocode(locstr)
    try:
      location = geolocator.reverse("{}, {}".format(str(location.raw['lat']), str(location.raw['lon'])), exactly_one=True)
      address = location.raw['address']
      cities = address.get('city', '').strip()
      countries = address.get('country', '').strip()
      states = address.get('state', '').strip()
    except:
      cities = ""
      countries = ""
  elif (loc_split_by_comma[-1].split(" ")[-1] == "Area") and (len(loc_split_by_comma) == 2):
    cities = loc_split_by_comma[0]
    states = loc_split_by_comma[-1].strip().split(" ")[0]
    geolocator = Nominatim(user_agent="geo12", timeout=3)
    location = geolocator.geocode("{}, {}".format(cities, states))
    try:
      location = geolocator.reverse("{}, {}".format(str(location.raw['lat']), str(location.raw['lon'])), exactly_one=True)
      address = location.raw['address']
      countries = address.get('country', '').strip()
    except:
      countries = ""
  elif (loc_split_by_space[0] == "Greater") and (locstr.split(",")[0].split(" ")[-1] == "Area"):
    locstr = loc_split_by_space[1] + "," + locstr.split(",")[-1]
    try:
      cities, states, countries = get_all_the_things(locstr)
    except:
      cities = ""
      states = None
      countries = None
  ##############################################################################
  try:
    place_entity = locationtagger.find_locations(text=locstr)
  except:
    return {
        "city":"",
        "state":"",
        "country":"",
        "country_code":"",
        "region":"",
        "region_code":""
    }

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
  ents = {"Central", "Capital", "Northern", "Southern", "Eastern", 
                "Western", "North", "South", "East", "West", "Region",
                "Province", "Division", "District", "Capital", "Governorate", 
                "Coast"}

  if states == None:
      if len(place_entity.regions) > 0:
          if place_entity.cities:
              if (place_entity.regions[0] == place_entity.cities[0]) and (place_entity.regions[0] not in ents):
                  if place_entity.other:
                      states = place_entity.other[0]
              elif place_entity.other:
                  if place_entity.other[0] in ents:
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
            try:
              if [ele for ele in place_entity.other if ele in ents][0]:
                try:
                  states = place_entity.regions[0]
                except:
                  states = i
            except:
              pass
      else:
          try:
              if [ele for ele in place_entity.other if ele in ents][0]:
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
          try:
            if [ele for ele in place_entity.other if ele in ents][0]:
                cities = ""
          except:
            pass
          if (cities == countries):
              for i in place_entity.other:
                try:
                  if [ele for ele in place_entity.other if ele in ents][0]:
                    temp.append(i)
                except:
                  pass
          try:
            if [ele for ele in temp if ele in ents][0]:
              pass
            else:
              cities = j
          except:
            pass
      else:
          try:
            if [ele for ele in place_entity.other if ele in ents][0]:
              pass
            else:
              cities = i
          except:
              cities = ""
      ##########################################################################
      #### SPECIAL CASE FOR JAPAN LOCATION 
      #########################################################################
      if cities == "Prefecture":
          cities = ""
          states = states + " " + "Prefecture"
      #########################################################################
      #### IF CITIES = STATES / CITIES = COUNTRIES WHICH IS NOT ACCEPTABLE
      ########################################################################
      if (cities == states) or (cities == countries) or (cities == None):
          cities = ""

      #########################################################################
      #### IF CURRENT RESULT JUST HAS A CITY
      #########################################################################
      try:
          if (cities != '') and (states == '') and (countries == ''):
              country_id, countries = get_country_code__using_city_only(cities)
      except:
          country_id, countries = "", ""

      #########################################################################
      #### IF ALL KEY IS NULL / EMPTY STRING 
      #########################################################################
      try:
          if (cities == '') and (states == '') and (countries == ''):
              _, _, countries = get_all_the_things(locstr)
      except:
          country_id, countries = "", ""

  ############################################################################
  # COUNTRY CODE
  ############################################################################
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
    try:
      continent_code = pc.country_alpha2_to_continent_code(country_id.strip())
    except:
      continent_code = ""
  else: continent_code = ""
  ##################################################################################
  # CONTINENT / REGION NAME
  ##################################################################################
  if continent_code:
      continent_name = pc.convert_continent_code_to_continent_name(continent_code.strip())
  else: continent_name = ""
  #########################################################################
  #### IF CURRENT RESULT HAS COUNTRY BUT COUNTRY/REGION CODE, AND
  #### REGION NAME IS EMPTY
  #########################################################################
  try:
      if (countries != '') and (country_id == '') and (continent_code == '') and (continent_name == '')\
      or (country_id == None) or (continent_code == None) or (continent_name == None):
          country_id = get_country_code_using_only_country(countries)
      if country_id:
        continent_code = pc.country_alpha2_to_continent_code(country_id.strip())
      else: 
        continent_code = ""
      if continent_code:
        continent_name = pc.convert_continent_code_to_continent_name(continent_code.strip())
      else: 
        continent_name = ""
  except:
      country_id, countries = "", ""

  ##################################################################################
  # STATE BACK-TRANSLATION
  ##################################################################################
  # states = GoogleTranslator(source="en", target=country_id.lower()).translate(states)

  if fuzz.ratio(states, countries) > 65.:
      states = ""

  if detect_language(countries) != "en":
      countries = GoogleTranslator(source="auto", target="en").translate(countries)

  return {"city": cities,
          "state": states,
          "country":countries,
          "country_code":country_id,
          "region":continent_name,
          "region_code":continent_code}

sample = "City of Fond du Lac"
loc = get_locations(sample)
print(loc)
