import streamlit as st
import geopandas as gpd
import pydeck as pdk

# Load shapefile
shapefile_path = "LUSE_FINAL.shp"  # Replace with the correct path
gdf = gpd.read_file(shapefile_path)

# Ensure CRS is WGS84 (EPSG:4326)
if gdf.crs != 'EPSG:4326':
    gdf = gdf.to_crs(epsg=4326)

# Convert to projected CRS for accurate centroid calculation
gdf_projected = gdf.to_crs(epsg=3857)
centroid_lat = gdf_projected.geometry.centroid.to_crs(epsg=4326).y.mean()
centroid_lon = gdf_projected.geometry.centroid.to_crs(epsg=4326).x.mean()

# Explode MultiPolygon geometries
gdf = gdf.explode(index_parts=True).reset_index(drop=True)

# Define heights and colors for different land use types
landuse_heights = {
    'bare': 15, 'built': 30, 'crops': 10, 'grass': 20, 'shrub_and_scrub': 25,
    'trees': 35, 'water': -5
}
landuse_colors = {
    'bare': [255, 192, 203], 'built': [255, 0, 0], 'crops': [255, 255, 0],
    'grass': [144, 238, 144], 'shrub_and_scrub': [255, 0, 255], 'trees': [0, 128, 0],
    'water': [0, 0, 255]
}

gdf['height'] = gdf['LANDUSE'].map(landuse_heights)
gdf['color'] = gdf['LANDUSE'].map(landuse_colors)

# MapTiler API Key
MAPTILER_API_KEY = "E6ZRsLot4eQsQImxowwm"

# MapTiler style URLs
map_styles = {
    "Hybrid": f"https://api.maptiler.com/maps/hybrid/style.json?key={MAPTILER_API_KEY}",
    "Streets": f"https://api.maptiler.com/maps/streets/style.json?key={MAPTILER_API_KEY}",
    "Outdoor": f"https://api.maptiler.com/maps/outdoor/style.json?key={MAPTILER_API_KEY}",
    "Topo Map": f"https://api.maptiler.com/maps/topo-v2/style.json?key={MAPTILER_API_KEY}",
    "Landscape": f"https://api.maptiler.com/maps/landscape/style.json?key={MAPTILER_API_KEY}",
}

# MapTiler terrain tile URL
terrain_url = f"https://api.maptiler.com/tiles/terrain-rgb-v2/{{z}}/{{x}}/{{y}}.png?key={MAPTILER_API_KEY}"

# Create terrain layer
terrain_layer = pdk.Layer(
    "TileLayer",
    tile_size=256,
    get_tile_url=terrain_url,
    opacity=1.0,
)

# Create land use polygon layers for swipe effect
polygon_layer_left = pdk.Layer(
    "PolygonLayer",
    data=gdf,
    get_polygon="geometry.coordinates",
    extruded=True,
    get_elevation="height",
    get_fill_color="color",
    elevation_scale=1,
    pickable=True,
    opacity=1,  # Left layer always visible
)

polygon_layer_right = pdk.Layer(
    "PolygonLayer",
    data=gdf,
    get_polygon="geometry.coordinates",
    extruded=True,
    get_elevation="height",
    get_fill_color="color",
    elevation_scale=1,
    pickable=True,
    opacity=0,  # Initially invisible, controlled by swipe
)

# Set initial view state
view_state = pdk.ViewState(
    latitude=centroid_lat,
    longitude=centroid_lon,
    zoom=12,
    pitch=45,
    bearing=30,
)

# Sidebar controls
map_style_enabled = st.checkbox("Enable Map Style", value=True)
terrain_enabled = st.checkbox("Show Terrain Layer", value=False)
show_landuse = st.checkbox("Show Land Use Polygons", value=True)
swipe_position = st.slider("Swipe Position", 0, 100, 50)

# Adjust swipe effect
polygon_layer_right.opacity = swipe_position / 100

# Define layers based on user selection
layers = []
if terrain_enabled:
    layers.append(terrain_layer)  # Add terrain layer if enabled
if show_landuse:
    layers.append(polygon_layer_left)
    layers.append(polygon_layer_right)

# Apply selected map style if enabled, else use a default blank style
selected_map_style = map_styles["Streets"] if not map_style_enabled else st.selectbox("Select Map Style", list(map_styles.keys()))

# Define the Deck
deck = pdk.Deck(
    layers=layers,
    initial_view_state=view_state,
    map_style=map_styles[selected_map_style] if map_style_enabled else None,  # Apply selected MapTiler style
)

# Display the map in Streamlit
st.pydeck_chart(deck)

# Debugging
st.write(f"Map Style Enabled: {map_style_enabled}")
st.write(f"Selected Map Style: {selected_map_style}")
st.write(f"Terrain Layer Enabled: {terrain_enabled}")
st.write(f"Swipe Position: {swipe_position}%")