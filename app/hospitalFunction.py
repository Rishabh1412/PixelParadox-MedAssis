import requests
import folium
from folium.plugins import MarkerCluster, HeatMap, MiniMap
from folium import Popup
import time

def generate_hospital_map(pin_code):
    def get_location_from_pincode(pincode):
        api_key = '907d895fce6e4117bcf921b134988f82'
        url = f"https://api.opencagedata.com/geocode/v1/json?q={pincode}&key={api_key}"
        headers = {
            'User-Agent': 'Medassis/1.0 (anujkaushal1068@gmail.com)'
        }
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"Error fetching location for pincode {pincode}: HTTP {response.status_code}")
            return None, None

        try:
            response_json = response.json()
        except ValueError as e:
            print(f"Error decoding JSON for pincode {pincode}: {e}")
            return None, None

        if response_json['results']:
            location = response_json['results'][0]['geometry']
            return float(location["lat"]), float(location["lng"])
        else:
            print(f"OpenCage API response for pincode {pincode}: {response_json}")
        return None, None

    def get_hospitals(location, radius):
        overpass_url = "http://overpass-api.de/api/interpreter"
        overpass_query = f"""
        [out:json];
        (
          node["amenity"="hospital"](around:{radius},{location[0]},{location[1]});
          way["amenity"="hospital"](around:{radius},{location[0]},{location[1]});
          relation["amenity"="hospital"](around:{radius},{location[0]},{location[1]});
        );
        out center;
        """
        response = requests.get(overpass_url, params={'data': overpass_query})
        
        if response.status_code != 200:
            print(f"Error fetching hospitals for location {location}: HTTP {response.status_code}")
            return []

        try:
            data = response.json()
        except ValueError as e:
            print(f"Error decoding JSON for hospitals at location {location}: {e}")
            return []

        hospitals = [
            {
                "name": element["tags"].get("name", "Unnamed Hospital"),
                "lat": element["lat"] if element["type"] == "node" else element["center"]["lat"],
                "lon": element["lon"] if element["type"] == "node" else element["center"]["lon"]
            }
            for element in data["elements"]
        ]
        
        if not hospitals:
            print(f"No hospitals found near location {location}")
        return hospitals

    location = get_location_from_pincode(pin_code)
    if location == (None, None):
        raise ValueError("Failed to retrieve the location for the provided pin code.")

    map_ = folium.Map(location=location, zoom_start=12)

    minimap = MiniMap()
    map_.add_child(minimap)

    folium.TileLayer(
        tiles='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        attr='Map data © OpenStreetMap contributors',
        name='OpenStreetMap'
    ).add_to(map_)

    marker_cluster = MarkerCluster().add_to(map_)

    heat_data = []
    hospitals = get_hospitals(location, 5000)
    if hospitals:
        for hospital in hospitals:
            folium.Marker(
                location=[hospital['lat'], hospital['lon']],
                popup=Popup(hospital['name'], max_width=300),
                icon=folium.Icon(icon='house-medical', prefix='fa', color='green')
            ).add_to(marker_cluster)
            heat_data.append([hospital['lat'], hospital['lon']])
    else:
        print(f"No hospitals found for pin code: {pin_code}")

    if heat_data:
        HeatMap(heat_data).add_to(map_)
    else:
        print("No heatmap data to add.")

    folium.Marker(
        location=location,
        popup=Popup("You are here", max_width=200),
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(map_)

    file_name = f'hospitals.html'
    map_.save(f"./app/templates/{file_name}")
    print(f"Interactive map with user location has been saved as '{file_name}'")

