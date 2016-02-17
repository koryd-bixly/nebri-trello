from setuptools import setup

setup(
    name='nebri-trello',
    version='0.9.0',
    description='nebri-trello is a nebri app to make communicating with and setting up trello webhooks easier.',
    url='https://github.com/koryd-bixly/nebri-trello',
    packages=['api', 'card_html_files', 'libraries', 'scripts'],
    author='koryd-bixly',
    install_requires=[
        'py-trello==0.4.3'
    ]
)