import json
import numpy as np
import folium
from scipy.spatial import Voronoi
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon

# Load data
with open('data.json', 'r') as f:
    data = json.load(f)

villages = data['villages']
hospitals = data['hospitals']

# Convert to NumPy arrays
village_coords = np.array([[v["Latitude"], v["Longitude"]] for v in villages])
hospital_coords = np.array([[h["Latitude"], h["Longitude"]] for h in hospitals])

# Compute Voronoi diagram
vor = Voronoi(hospital_coords)

# Function to check if a village is in a grey zone
def is_grey_zone(village):
    village_point = Point(village["Latitude"], village["Longitude"])
    
    for region_index in vor.point_region:
        region = vor.regions[region_index]
        
        # Ensure region is valid and closed
        if -1 not in region and len(region) > 2:
            polygon = Polygon([vor.vertices[i] for i in region])
            if polygon.contains(village_point):
                return False  # Village is inside a hospital region
    
    return True  # Village is outside all hospital regions (Grey Zone)

# Identify grey zone villages
grey_zones = [v for v in villages if is_grey_zone(v)]

# Create a Folium map centered at the first village
map_center = [village_coords[0][0], village_coords[0][1]]
m = folium.Map(location=map_center, zoom_start=10)

# Plot Villages
for v in villages:
    color = 'gray' if v in grey_zones else 'blue'
    folium.CircleMarker(
        location=[v["Latitude"], v["Longitude"]],
        radius=5,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.6,
        popup=f"{v['name']} ({'Grey Zone' if color == 'gray' else 'Normal'})"
    ).add_to(m)

# Plot Hospitals
for h in hospitals:
    folium.Marker(
        location=[h["Latitude"], h["Longitude"]],
        popup=h["Name of Hospital"],
        icon=folium.Icon(color='red', icon="plus-sign")
    ).add_to(m)

# Save the map
m.save("voronoi_grey_zone.html")
print("Grey zone detection complete. Check voronoi_grey_zone.html")

