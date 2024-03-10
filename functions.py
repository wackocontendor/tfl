import json
import requests
import os

#Authentication keys
app_id = os.environ.get('TFL_API_ID')
app_keys = os.environ.get('TFL_API_KEY')

#TfL API URL
url_prefix = "https://api.tfl.gov.uk/"

def get_available_modes():
    return ",".join(["cable-car","dlr","elizabeth-line","overground","tram","tube"])

def get_available_lines():
    return ['bakerloo', 'central', 'circle', 'district', 'dlr', 'elizabeth', 'hammersmith-city', 'jubilee', 'london-cable-car', 'london-overground', 'metropolitan', 'northern', 'piccadilly', 'tram', 'victoria', 'waterloo-city']

#Return all the available modes on the network
def get_all_modes():
    modes_response = requests.get(f'{url_prefix}Journey/Meta/Modes')
    modes_content = json.loads(modes_response.content)
    modes_list = []
    for mode in range(len(modes_content)):
        if modes_content[mode]['isTflService'] == False:
            continue
        modes_list.append(modes_content[mode]['modeName'])
    return modes_list

#Return all the lines for the given modes
def get_all_lines():
    search_modes = get_available_modes()
    lines_response = requests.get(f'{url_prefix}line/mode/{search_modes}?app_id={app_id}&app_key={app_keys}')
    lines_content = json.loads(lines_response.content)
    lines_list = []
    for line in range(len(lines_content)):
        lines_list.append(lines_content[line]['id'])
    return lines_list
