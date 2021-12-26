from distutils.core import setup
setup(
  name = 'chess-game',
  packages = ['chess-game'],
  version = '0.1',
  license='GPL-3.0+',
  description = 'A simple chess library',
  author = 'Utkrisht Sinha',
  author_email = '',
  url = 'https://github.com/Utkrisht-1997/chess-game',
  download_url = 'https://github.com/user/reponame/archive/v_01.tar.gz',
  keywords = ['chess', 'game', 'python'],
  install_requires=[
          'validators',
          'beautifulsoup4',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha', 
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
  ],
)
