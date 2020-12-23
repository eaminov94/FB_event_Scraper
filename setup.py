from setuptools import setup, find_packages

setup(
    name         = 'project',
    version      = '1.0',
    packages     = find_packages(),
    package_data = {'FB_events': ['data/*']
    },
    entry_points = {'scrapy': ['settings = FB_events.settings']},
)
