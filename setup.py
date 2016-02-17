import os, sys
from distutils.core import setup
from setuptools.command.install import install as _install


def _post_install(dir):
    for (dirpath, dirnames, filenames) in os.walk(dir):
        if dirpath == dir + 'api':
            print dirpath, filenames
            for file in filenames:
                os.rename('%s/%s' % (dirpath, file), '/home/nebrios-sftp/api/%s' % file)
        if dirpath == dir + 'card_html_files':
            for file in filenames:
                os.rename('%s/%s' % (dirpath, file), '/home/nebrios-sftp/card_html_files/%s' % file)
        if dirpath == dir + 'libraries':
            for file in filenames:
                os.rename('%s/%s' % (dirpath, file), '/home/nebrios-sftp/libraries/%s' % file)
        if dirpath == dir + 'scripts':
            for file in filenames:
                os.rename('%s/%s' % (dirpath, file), '/home/nebrios-sftp/scripts/%s' % file)


class install(_install):
    def run(self):
        _install.run(self)
        self.execute(_post_install, (self.install_lib,),
                     msg="Running post install task %s" % self.install_lib)

setup(
    name='nebri-trello',
    version='0.9.0',
    description='nebri-trello is a nebri app to make communicating with and setting up trello webhooks easier.',
    url='https://github.com/koryd-bixly/nebri-trello',
    packages=['api', 'card_html_files', 'libraries', 'scripts'],
    author='koryd-bixly',
    install_requires=[
        'py-trello==0.4.3',
        'iso8601==0.1.11'
    ],
    cmdclass={'install': install}
)