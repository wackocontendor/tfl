import json
import requests
import math
import pandas as pd
import os
from My_Functions import get_available_modes
from My_Functions import get_available_lines

#These are the authentication keys to add to the end of any TfL API search request (it increases the number of calls per minute that you're allowed)
app_id = os.environ.get('TFL_API_ID')
app_keys = os.environ.get('TFL_API_KEY')

#Set the list of TfL modes to search through
search_modes = get_available_modes()

#Valid list of lines on the modes
valid_lines = get_available_lines()

#Ask the user to search for a string
search_term = input('\nEnter a search term to return a list of stations that match: ')

#URL to search
response = requests.get(f'https://api.tfl.gov.uk/Stoppoint/Search/{search_term}?modes={search_modes}&app_id={app_id}&app_key={app_keys}')

#Load the output from the URL into a JSON
data_content = json.loads(response.content)

station_id = ''
station_name = ''

#Ask the user to choose the number in the list that matches the station they were looking for, unless only one was returned
if data_content['total'] == 0:
     print("\nYour search term didn't return any results.")

elif data_content['total'] == 1:
     station_id = data_content['matches'][0]['id']
     station_name = data_content['matches'][0]['name']

else:
     #Tell the user how many stations matched their search
     print('\nNumber of stations that match the search term:',data_content['total'],'\n')

     #Loop through all the results of the search term and add each to a dictionary containing the station id and station name
     station_dict = {}

     for x in range(1,int(len(data_content['matches']))+1):
          station_dict.update({x: {'station_id': '', 'station_name': ''}})
          station_dict[x]['station_id'] = data_content['matches'][x-1]['id']
          station_dict[x]['station_name'] = data_content['matches'][x-1]['name']
          print(x,station_dict[x]['station_name'])

     station_chosen = input('\nSelect a number from the options above: ')

     station_id = station_dict[int(station_chosen)]['station_id']
     station_name = station_dict[int(station_chosen)]['station_name']

#Create a list of the lines at the stop

lines_at_stop_response = requests.get(f'https://api.tfl.gov.uk/Stoppoint/{station_id}?app_id={app_id}&app_key={app_keys}')
lines_at_stop_content = json.loads(lines_at_stop_response.content)
lines_at_stop = []

for line in range(len(lines_at_stop_content['lines'])):
     if lines_at_stop_content['lines'][line]['id'] in valid_lines:
          lines_at_stop.append(lines_at_stop_content['lines'][line]['id'])

chosen_line = ''

if len(lines_at_stop) == 1:
     chosen_line = lines_at_stop[0]

else:
     print(f'\nPlease select the line you want to view the timetable for at {station_name}:\n')

     for line in lines_at_stop:
          print(lines_at_stop.index(line)+1,line)

     chosen_line_input = input('\nSelect a number from the options above: ')
     chosen_line = lines_at_stop[int(chosen_line_input)-1]

#for HUBs, find the right naptan id
if station_id[:3] == 'HUB':
     #find the mode for the chosen line
     mode_response = requests.get(f'https://api.tfl.gov.uk/Line/{chosen_line}')
     mode_content = json.loads(mode_response.content)

     line_mode = mode_content[0]['modeName']

     #search through the children of the HUB to find the naptan id matching the mode
     for child in range(len(lines_at_stop_content['children'])):
          if line_mode in lines_at_stop_content['children'][child]['modes']:
               station_id = lines_at_stop_content['children'][child]['naptanId']

arrivals_response = requests.get(f'https://api.tfl.gov.uk/Line/{chosen_line}/Arrivals/{station_id}?app_id={app_id}&app_key={app_keys}')
arrivals_content = json.loads(arrivals_response.content)

arrivalsdict = {'Platform': [],
                   'Destination': [],
                   'ETA': []}

for train in range(len(arrivals_content)):
     arrivalsdict['Platform'].append(arrivals_content[train]['platformName'])
     arrivalsdict['Destination'].append(arrivals_content[train]['destinationName'])
     arrivalsdict['ETA'].append(math.floor(arrivals_content[train]['timeToStation']/60))

df = pd.DataFrame(arrivalsdict)
df.sort_values(by = ['Platform', 'ETA'], ascending = [True, True], inplace=True)

print('\n',df.to_string(index=False))
