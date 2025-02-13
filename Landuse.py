import streamlit as st
import geopandas as gpd
import pydeck as pdk

# Load shapefile
shapefile_path = "LUSE_FINAL.shp"
gdf = gpd.read_file(shapefile_path)

# Reproject if necessary
if gdf.crs != 'EPSG:4326':
    gdf = gdf.to_crs(epsg=4326)

# Explode MultiPolygon geometries
gdf = gdf.explode(index_parts=True).reset_index(drop=True)

# Define heights and colors
landuse_heights = {'bare': 15, 'built': 30, 'crops': 10, 'grass': 20, 'shrub_and_scrub': 25, 'trees': 35, 'water': -5}
landuse_colors = {'bare': [255, 192, 203], 'built': [255, 0, 0], 'crops': [255, 255, 0], 'grass': [144, 238, 144], 
                  'shrub_and_scrub': [255, 0, 255], 'trees': [0, 128, 0], 'water': [0, 0, 255]}

gdf['height'] = gdf['LANDUSE'].map(landuse_heights)
gdf['color'] = gdf['LANDUSE'].map(landuse_colors)

# MapTiler API Key
MAPTILER_API_KEY = "E6ZRsLot4eQsQImxowwm"

# Create Polygon Layer
polygon_layer = pdk.Layer(
    'PolygonLayer',
    data=gdf,
    get_polygon='geometry.coordinates',
    extruded=True,
    get_elevation='height',
    get_fill_color='color',
    elevation_scale=1,
    pickable=True,
)

# MapTiler Styles (without base maps)
map_styles = {
    "Hybrid": f"https://api.maptiler.com/maps/hybrid/style.json?key={MAPTILER_API_KEY}",
    "Streets": f"https://api.maptiler.com/maps/streets/style.json?key={MAPTILER_API_KEY}",
    "Outdoor": f"https://api.maptiler.com/maps/outdoor/style.json?key={MAPTILER_API_KEY}",
    "Topo Map": f"https://api.maptiler.com/maps/topo-v2/style.json?key={MAPTILER_API_KEY}",
    "Landscape": f"https://api.maptiler.com/maps/landscape/style.json?key={MAPTILER_API_KEY}",
    "Terrain": f"https://api.maptiler.com/maps/terrain/style.json?key={MAPTILER_API_KEY}"
}

# Map Style Selection
map_style = st.selectbox("Select Map Style", list(map_styles.keys()))

# Set initial view state
view_state = pdk.ViewState(
    latitude=gdf.geometry.centroid.y.mean(),
    longitude=gdf.geometry.centroid.x.mean(),
    zoom=10,
    pitch=45,
    bearing=30,
)

# Toggle Land Use Polygons
show_landuse = st.checkbox("Show Land Use Polygons", value=True)

# Create PyDeck Map
layers = [polygon_layer] if show_landuse else []

# Streamlit Slider to control the swipe
swipe_position = st.slider("Swipe Position", 0, 100, 50)

# Create a swipeable map layer
swipe_layer = pdk.Layer(
    'PolygonLayer',
    data=gdf,
    get_polygon='geometry.coordinates',
    extruded=True,
    get_elevation='height',
    get_fill_color='color',
    elevation_scale=1,
    pickable=True,
    visible=True,  # Control visibility with the slider
    opacity=swipe_position / 100,
)

# Add swipe layer
layers.append(swipe_layer)

deck = pdk.Deck(
    layers=layers,
    initial_view_state=view_state,
    map_style=map_styles[map_style],  # Selecting MapTiler style dynamically
)

# Display the map with the swipe effect
st.pydeck_chart(deck)