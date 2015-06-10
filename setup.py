from distutils.core import setup

__author__ = 'Alex Haslehurst'

setup(
    name='retro_scrapers',
    version='0.1',
    packages=['axh', 'axh.retro', 'axh.retro.scrapers', 'axh.retro.scrapers.tgdb'],
    namespace_packages=['axh', 'axh.retro'],
    url='https://github.com/axle-h/retro-scrapers',
    license='',
    author='Alex Haslehurst',
    author_email='alex.haslehurst@gmail.com',
    description='Collection of retro gaming meta data scrapers'
)
