import json
import requests
import math
import pandas as pd
import os

# Create a list of all the available modes on the TfL network
def get_all_modes(url_prefix, app_id, app_keys):
    modes_response = requests.get(f'{url_prefix}Journey/Meta/Modes?app_id={app_id}&app_key={app_keys}')
    modes_content = json.loads(modes_response.content)
    modes_list = []
    for mode in range(len(modes_content)):
        if modes_content[mode]['isTflService'] == False:
            continue
        modes_list.append(modes_content[mode]['modeName'])
    return modes_list

# Create a list of all the lines for selected modes
def get_lines_modes(search_modes, url_prefix, app_id, app_keys):
    search_modes_parameter = ",".join(search_modes)
    lines_response = requests.get(f'{url_prefix}line/mode/{search_modes_parameter}?app_id={app_id}&app_key={app_keys}')
    lines_content = json.loads(lines_response.content)
    lines_list = []
    for line in range(len(lines_content)):
        lines_list.append(lines_content[line]['id'])
    return lines_list

# Create a list of all the stations and IDs for selected modes
def get_stations_modes(search_modes, url_prefix, app_id, app_keys):
     None

# Create a list of all the lines for selected station that are within the list of accepted lines
def get_lines_station(station_id, valid_lines, url_prefix, app_id, app_keys):
     lines_at_stop = []
     lines_at_stop_response = requests.get(f'{url_prefix}Stoppoint/{station_id}?app_id={app_id}&app_key={app_keys}')
     lines_at_stop_content = json.loads(lines_at_stop_response.content)
     for line in range(len(lines_at_stop_content['lines'])):
          if lines_at_stop_content['lines'][line]['id'] in valid_lines:
               lines_at_stop.append(lines_at_stop_content['lines'][line]['id'])

def get_arrivals_station(station_id, line_id, url_prefix, app_id, app_keys):
     arrivals_dict = {'Platform': [],
               'Destination': [],
               'ETA': []}
     arrivals_response = requests.get(f'{url_prefix}Line/{line_id}/Arrivals/{station_id}?app_id={app_id}&app_key={app_keys}')
     arrivals_content = json.loads(arrivals_response.content)
     for train in range(len(arrivals_content)):
          arrivals_dict['Platform'].append(arrivals_content[train]['platformName'])
          arrivals_dict['Destination'].append(arrivals_content[train]['destinationName'])
          arrivals_dict['ETA'].append(math.floor(arrivals_content[train]['timeToStation']/60))
     return arrivals_dict

app_id = os.environ.get('TFL_API_ID')
app_keys = os.environ.get('TFL_API_KEY')
url_prefix = "https://api.tfl.gov.uk/"
search_modes = ["dlr", "elizabeth-line", "overground", "tram" ,"tube"]

# load a file into a dataframe that has a list of all the stations and their IDs

# get user to select a station and store the station id

chosen_station = "xx"
chosen_station_id = "940GZZLUNGW"

# get a list of all the valid lines for the given search modes

valid_lines = get_lines_modes(search_modes, url_prefix, app_id, app_keys)

# get a list of all the valid lines at that stop

lines_at_station = get_lines_station(chosen_station_id, valid_lines, url_prefix, app_id, app_keys)

# get user to choose a line or prepopulate if only 1

chosen_line_id = "jubilee"

# get a list of arrivals for the chosen line and station

chosen_arrivals = get_arrivals_station(chosen_station_id, chosen_line_id, url_prefix, app_id, app_keys)

df = pd.DataFrame(chosen_arrivals)

df.sort_values(by = ['Platform', 'ETA'], ascending = [True, True], inplace=True)

print('\n',df.to_string(index=False))

# What to do with HUBs - hopefully won't need this code if we can get the right ID in the first lookup
# if station_id[:3] == 'HUB':
#      #find the mode for the chosen line
#      mode_response = requests.get(f'https://api.tfl.gov.uk/Line/{chosen_line}')
#      mode_content = json.loads(mode_response.content)

#      line_mode = mode_content[0]['modeName']

#      #search through the children of the HUB to find the naptan id matching the mode
#      for child in range(len(lines_at_stop_content['children'])):
#           if line_mode in lines_at_stop_content['children'][child]['modes']:
#                station_id = lines_at_stop_content['children'][child]['naptanId']