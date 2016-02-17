import os, sys
from distutils.core import setup
from setuptools.command.install import install as _install


def _post_install(dir):



class install(_install):
    def run(self):
        _install.run(self)
        self.execute(_post_install, (self.install_lib,),
                     msg="Running post install task %s" % self.install_data)

setup(
    name='nebri-trello',
    version='0.9.0',
    description='nebri-trello is a nebri app to make communicating with and setting up trello webhooks easier.',
    url='https://github.com/koryd-bixly/nebri-trello',
    packages=['api', 'card_html_files', 'libraries', 'scripts'],
    author='koryd-bixly',
    install_requires=[
        'py-trello==0.4.3'
    ],
    cmdclass={'install': install}
)