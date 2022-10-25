from setuptools import setup

setup(name='WifiSelectorHotspot',
      version='0.1',
      description='Utility to select WiFi network over WiFi Hotspot',
      author='Basil',
      author_email='basil.huber@gmail.com',
      packages=['wifi_selector_hotspot'],
      install_requires=['flask'],
      entry_points={'console_scripts': ['wifi_selector_hotspot=wifi_selector_hotspot.main:main']},
      include_package_data=True,
      zip_safe=False)
