from setuptools import setup, find_packages

setup(
    name         = 'project',
    version      = '1.0',
    packages     = find_packages(),
    package_data = {'FB_events': ['data/*']
    },
    entry_points = {'scrapy': ['settings = FB_events.settings']},
)
[settings]
default = FB_events.settings

[deploy]
#url = http://localhost:6800/
project = FB_events
