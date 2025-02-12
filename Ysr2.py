import streamlit as st
import geopandas as gpd
import pydeck as pdk

# Load your shapefile (make sure it’s in the same directory or adjust the path)
shapefile_path = "LUSE_FINAL.shp"  # Make sure the shapefile is in the repo
gdf = gpd.read_file(shapefile_path)

# Reproject to EPSG:4326 (WGS84) if necessary
if gdf.crs != 'EPSG:4326':
    gdf = gdf.to_crs(epsg=4326)

# Explode MultiPolygon geometries into individual Polygon geometries
gdf = gdf.explode(index_parts=True).reset_index(drop=True)

# Define heights for each LANDUSE category
landuse_heights = {
    'bare': 15, 'built': 30, 'crops': 10, 'grass': 20,
    'shrub_and_scrub': 25, 'trees': 35, 'water': -5
}

# Define colors for each LANDUSE category (in RGB format)
landuse_colors = {
    'bare': [255, 192, 203], 'built': [255, 0, 0], 'crops': [255, 255, 0],
    'grass': [144, 238, 144], 'shrub_and_scrub': [255, 0, 255], 'trees': [0, 128, 0], 'water': [0, 0, 255]
}

# Assign heights and colors
gdf['height'] = gdf['LANDUSE'].map(landuse_heights)
gdf['color'] = gdf['LANDUSE'].map(landuse_colors)

# Replace with your MapTiler API key
MAPTILER_API_KEY = "E6ZRsLot4eQsQImxowwm"

# Create the PyDeck layers
polygon_layer = pdk.Layer(
    'PolygonLayer',
    data=gdf,
    get_polygon='geometry.coordinates',
    extruded=True,
    get_elevation='height',
    get_fill_color='color',
    elevation_scale=2,
    pickable=True,
)

# Tile Layers for different base maps
tile_layer_satellite = pdk.Layer(
    'TileLayer',
    data=None,
    get_tile_data=f'https://api.maptiler.com/maps/satellite/{{z}}/{{x}}/{{y}}.jpg?key={MAPTILER_API_KEY}',
    pickable=False,
    tile_size=256,
)

tile_layer_osm = pdk.Layer(
    'TileLayer',
    data=None,
    get_tile_data='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    pickable=False,
    tile_size=256,
)

# Set the view state to center on the data
view_state = pdk.ViewState(
    latitude=gdf.geometry.centroid.y.mean(),
    longitude=gdf.geometry.centroid.x.mean(),
    zoom=10,
    pitch=45,
    bearing=30,
)

# Function to create a PyDeck map with a given tile layer and polygon layer
def create_map(tile_layer, polygon_layer=None):
    layers = [tile_layer]
    if polygon_layer:
        layers.append(polygon_layer)
    
    deck = pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        map_style="https://api.maptiler.com/maps/hybrid/style.json?key=" + MAPTILER_API_KEY,  # Adding map style
    )
    return deck

# Streamlit App
st.title("Interactive Land Use Visualization with Layer Controls")

# Layer Control to toggle base maps and polygon layer
show_landuse = st.checkbox("Show Land Use Polygons", value=True)
base_map = st.selectbox("Select Base Map", ["Satellite", "OpenStreetMap"])

# Selecting the base map layer
if base_map == "Satellite":
    tile_layer = tile_layer_satellite
elif base_map == "OpenStreetMap":
    tile_layer = tile_layer_osm

# Create the map with the selected base map and polygon layer visibility
deck = create_map(tile_layer, polygon_layer if show_landuse else None)

# Display the map
st.pydeck_chart(deck)
