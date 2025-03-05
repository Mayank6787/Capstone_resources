import json
import folium

# Load village and hospital data
with open('data.json', 'r') as f:
    data = json.load(f)

villages = data.get('villages', [])
hospitals = data.get('hospitals', [])

# Ensure there are villages to center the map
if not villages:
    raise ValueError("No village data found. Please check the data.json file.")

# Create a map centered around the first village
map_center = [villages[0]['Latitude'], villages[0]['Longitude']]
m = folium.Map(location=map_center, zoom_start=10)

# Function to add markers to the map
def add_markers(data_list, color, icon=None):
    for item in data_list:
        folium.Marker(
            location=[item['Latitude'], item['Longitude']],
            popup=item['name'],
            icon=folium.Icon(color=color, icon=icon) if icon else folium.Icon(color=color)
        ).add_to(m)


def add_markers_hospitals(data_list, color, icon=None):
    for item in data_list:
        folium.Marker(
            location=[item['Latitude'], item['Longitude']],
            popup=item['Name of Hospital'],
            icon=folium.Icon(color=color, icon=icon) if icon else folium.Icon(color=color)
        ).add_to(m)

# Add village markers (blue)
add_markers(villages, color='blue')

# Add hospital markers (red with plus sign icon)
add_markers_hospitals(hospitals, color='red', icon="plus-sign")

# Save the map
m.save("map.html")
print("Map has been saved as map.html")
