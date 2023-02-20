name = 'wavetherfinder'
version = '0.0.1'

requires = ['geopy', 'ephem', 'requests', 'folium', 'json']

variants = [['platform-linux']]

def commands():
    env.PYTHONPATH.prepend("{root}/python")