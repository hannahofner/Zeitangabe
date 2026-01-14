import requests
import json
from datetime import datetime

# Official Wiener Linien API endpoint for real-time monitor
API_URL = "http://www.wienerlinien.at/ogd_realtime/monitor"

def get_departures(stop_id):
    """
    Fetches upcoming departures for a given stop ID (or comma-separated IDs).
    Returns a list of dictionaries with line, direction, and countdown.
    """
    # Split the ID string into a list of RBL IDs
    rbl_ids = [id.strip() for id in str(stop_id).split(',')]
    
    # Construct params with multiple 'rbl' keys
    # requests supports list of tuples for multiple keys
    params = [('activateTrafficInfo', 'stoerungkurz')]
    for rbl in rbl_ids:
        params.append(('rbl', rbl))
    
    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

    departures = []
    
    # Parse the nested JSON structure
    # data -> data -> monitors -> lines -> departures -> departureTime -> countdown
    
    if 'data' not in data or 'monitors' not in data['data']:
        return []
        
    for monitor in data['data']['monitors']:
        for line in monitor.get('lines', []):
            line_name = line.get('name')
            direction = line.get('towards')
            
            # departures is a dict containing a list under key 'departure'
            departures_container = line.get('departures', {})
            departure_list = departures_container.get('departure', [])
            
            for dep in departure_list:
                # The API structure: 'departureTime' -> 'countdown'
                
                dep_info = dep.get('departureTime', {})
                countdown = dep_info.get('countdown')
                
                if countdown is not None:
                    departures.append({
                        'line': line_name,
                        'direction': direction,
                        'countdown': countdown
                    })
                    
    # Sort by countdown time
    departures.sort(key=lambda x: x['countdown'])
    
    return departures

if __name__ == '__main__':
    # Test with Stephansplatz (approximate ID, or one of the platforms)
    # 60200624 is often used for examples
    print(get_departures('60200624'))
