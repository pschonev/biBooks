from distutils.core import setup
from setuptools import find_packages
from itertools import chain
import os

# User-friendly description from README.md
current_directory = os.path.dirname(os.path.abspath(__file__))
try:
    with open(os.path.join(current_directory, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
except Exception:
    long_description = ''


EXTRAS_REQUIRE = {'rus_stress':['udar', 'tqdm'],
					'pre_process':['pysbd'],
					'scraping':['beautifulsoup4', 'requests']}
					
EXTRAS_REQUIRE['full'] = list(set(chain(*EXTRAS_REQUIRE.values())))

setup(
	name='biBooks',

	packages=find_packages('.'),

	version='0.1',

	license='MIT',

	description='This repository allows the creation of an ebook with text passages alternating in two languages for the purpose of language learning.',
	
	long_description=long_description,

	long_description_content_type='text/markdown',

	author='Philipp Schoneville',

	author_email='ph.schoneville@gmail.com',

	url='https://github.com/pschonev',

	download_url='https://github.com/pschonev/biBooks',

	keywords=['language learning', 'learning', 'ebook'],

	install_requires=['jsonargparse', 'regex', 'numpy', 'cython', 'torch', 'fastBPE', 'transliterate'],

	extras_require=EXTRAS_REQUIRE,

	classifiers=['Development Status :: 4 - Beta', 'Operating System :: POSIX :: Linux', 'Programming Language :: Python']
)
