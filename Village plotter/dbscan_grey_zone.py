import json
import numpy as np
import folium
from sklearn.cluster import DBSCAN
from geopy.distance import geodesic
from scipy.spatial import ConvexHull
from shapely.geometry import Polygon, Point, MultiPoint
from sklearn.cluster import DBSCAN

# Load data
with open('data.json', 'r') as f:
    data = json.load(f)

villages = data['villages']
hospitals = data['hospitals']

# Convert to NumPy arrays
village_coords = np.array([[v["Latitude"], v["Longitude"]] for v in villages])
hospital_coords = np.array([[h["Latitude"], h["Longitude"]] for h in hospitals])

# Add these constants at the top after imports
INDIA_BOUNDS = {
    'min_lat': 6.5546079,
    'max_lat': 35.6745457,
    'min_lon': 68.1113787,
    'max_lon': 97.395561
}

# Function to check if a village is within 5km of any hospital
def is_near_hospital(village_coord, hospitals):
    for hospital in hospitals:
        distance = geodesic(
            (village_coord[0], village_coord[1]),
            (hospital["Latitude"], hospital["Longitude"])
        ).kilometers
        if distance <= 5:  # 5km radius
            return True
    return False

# Separate villages into red (no hospital) and green (near hospital) zones
red_villages = []
green_villages = []
for v in villages:
    village_coord = [v["Latitude"], v["Longitude"]]
    if is_near_hospital(village_coord, hospitals):
        green_villages.append(village_coord)
    else:
        red_villages.append(village_coord)

# Convert to numpy array for processing
red_villages_array = np.array(red_villages)

# Function to create grey zones from red villages
def create_grey_zones(red_villages_array):
    if len(red_villages_array) < 4:
        return []
    
    # Use DBSCAN to cluster nearby red villages
    clustering = DBSCAN(eps=0.05, min_samples=3).fit(red_villages_array)
    
    grey_zones = []
    for label in set(clustering.labels_):
        if label == -1:  # Skip noise points
            continue
            
        # Get points in this cluster
        cluster_points = red_villages_array[clustering.labels_ == label]
        
        if len(cluster_points) >= 4:  # Only create zones with at least 4 points
            try:
                # Create convex hull for the cluster
                hull = ConvexHull(cluster_points)
                hull_points = cluster_points[hull.vertices]
                
                # Create polygon with buffer
                polygon = Polygon(hull_points).buffer(0.01)  # Add small buffer
                grey_zones.append(polygon)
            except:
                continue
                
    return grey_zones

# Create grey zones
grey_zones = create_grey_zones(red_villages_array)

# Map setup
min_lat = min(min(v["Latitude"] for v in villages), min(h["Latitude"] for h in hospitals))
max_lat = max(max(v["Latitude"] for v in villages), max(h["Latitude"] for h in hospitals))
min_lon = min(min(v["Longitude"] for v in villages), min(h["Longitude"] for h in hospitals))
max_lon = max(max(v["Longitude"] for v in villages), max(h["Longitude"] for h in hospitals))

center_lat = (min_lat + max_lat) / 2
center_lon = (min_lon + max_lon) / 2

padding = 0.02
bounds = [
    [min_lat - padding, min_lon - padding],
    [max_lat + padding, max_lon + padding]
]

# Create map
map = folium.Map(
    location=[20.5937, 78.9629],  # Center of India
    zoom_start=5,
    min_zoom=5,
    max_zoom=15
)

# Set strict bounds for India
map.fit_bounds([
    [INDIA_BOUNDS['min_lat'], INDIA_BOUNDS['min_lon']],
    [INDIA_BOUNDS['max_lat'], INDIA_BOUNDS['max_lon']]
])

# Add grey zones to map
for zone in grey_zones:
    coords = [[y, x] for x, y in zone.exterior.coords]
    folium.Polygon(
        locations=coords,
        color='grey',
        fill=True,
        fill_color='grey',
        fill_opacity=0.3,
        popup='Grey Zone (Area without hospital coverage)',
        weight=2
    ).add_to(map)

# Plot villages
for v in villages:
    village_coord = [v["Latitude"], v["Longitude"]]
    
    # Find nearest hospital and its distance
    nearest_hospital = None
    min_distance = float('inf')
    for h in hospitals:
        distance = geodesic(
            village_coord,
            [h["Latitude"], h["Longitude"]]
        ).kilometers
        if distance < min_distance:
            min_distance = distance
            nearest_hospital = h
    
    is_green_zone = min_distance <= 5
    
    if is_green_zone:
        # Green villages - show as markers
        folium.CircleMarker(
            village_coord,
            popup=f'''
                <b>{v['name']}</b><br>
                Nearest Hospital: {nearest_hospital['Name of Hospital']}<br>
                Distance: {min_distance:.2f} km
            ''',
            color='green',
            fill=True,
            fill_color='green',
            fill_opacity=0.7,
            radius=8,
            weight=2
        ).add_to(map)
    else:
        # Grey circle for unserved area
        folium.Circle(
            village_coord,
            radius=5000,
            popup=f'''
                <b>{v['name']}</b><br>
                Nearest Hospital: {nearest_hospital['Name of Hospital']}<br>
                Distance: {min_distance:.2f} km (outside 5km radius)
            ''',
            color='grey',
            fill=True,
            fill_color='grey',
            fill_opacity=0.2,
            weight=2
        ).add_to(map)
        
        # Red dot for unserved village
        folium.CircleMarker(
            village_coord,
            popup=f'''
                <b>{v['name']}</b><br>
                Nearest Hospital: {nearest_hospital['Name of Hospital']}<br>
                Distance: {min_distance:.2f} km
            ''',
            color='red',
            fill=True,
            fill_color='red',
            fill_opacity=0.7,
            radius=4,
            weight=2
        ).add_to(map)

# Plot hospitals with coverage radius
for h in hospitals:
    hospital_coord = [h["Latitude"], h["Longitude"]]
    
    # 5km radius circle for hospital coverage (green with low opacity)
    hospital_circle = folium.Circle(
        hospital_coord,
        radius=5000,
        color='green',
        fill=True,
        fill_color='green',
        fill_opacity=0.1,  # Very light green
        weight=2,
        popup=f"Coverage area of {h['Name of Hospital']}"
    ).add_to(map)
    
    # Hospital marker
    hospital_icon = folium.DivIcon(
        html='''
            <div style="
                background-color: white;
                border: 3px solid green;
                border-radius: 50%;
                text-align: center;
                width: 25px;
                height: 25px;
                line-height: 20px;
                font-weight: bold;
            ">H</div>
        '''
    )
    
    folium.Marker(
        hospital_coord,
        popup=f'''
            <b>{h['Name of Hospital']}</b><br>
            Coverage Radius: 5km
        ''',
        icon=hospital_icon
    ).add_to(map)

# Update the legend
legend_html = '''
<div style="position: fixed; 
            bottom: 50px; right: 50px; width: 300px; 
            border:2px solid grey; z-index:9999; background-color:white;
            opacity:0.9;
            padding: 10px;
            font-size: 14px;">
    <h4 style="margin-top:0;">Map Legend</h4>
    <p><i style="border: 2px solid green; background: white; width: 20px; height: 20px; border-radius: 50%; display: inline-block; text-align: center; line-height: 18px;">H</i> Hospital (5km coverage area)</p>
    <p><i style="background: green; width: 15px; height: 15px; border-radius: 50%; display: inline-block;"></i> Village within hospital coverage (5km)</p>
    <p><i style="background: red; width: 15px; height: 15px; border-radius: 50%; display: inline-block;"></i> Village without hospital coverage</p>
    <p><i style="background: grey; opacity: 0.3; width: 15px; height: 15px; display: inline-block;"></i> 5km radius around uncovered village</p>
    <hr style="margin: 5px 0;">
    <p style="font-size: 12px;"><i>Click on markers for detailed information</i></p>
</div>
'''
map.get_root().html.add_child(folium.Element(legend_html))

# Add bounds restriction
map.options['maxBounds'] = [
    [INDIA_BOUNDS['min_lat'], INDIA_BOUNDS['min_lon']],
    [INDIA_BOUNDS['max_lat'], INDIA_BOUNDS['max_lon']]
]
map.options['maxBoundsViscosity'] = 1.0

# Save the map
map.save("dbscan_grey_zone.html")
print("Grey zone detection complete. Check dbscan_grey_zone.html")
