
from configobj import ConfigObj

# Load the .ini file
config = ConfigObj('/home/link/.config/dunst/dunstrc')

# Access values
# print(config['Settings']['theme'])

print(config)
# Modify and preserve comments
# config['Settings']['theme'] = 'light'
config.filename = "example.ini"
config.write()
