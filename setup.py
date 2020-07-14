from setuptools import setup, find_packages

with open('README.md', 'r') as fp:
    long_description = fp.read()

entrypoints = {
    'console_scripts': [
        'cloudmonitor=cloudmonitor.cmd.cloudmonitor:main'
    ]
}

setup(
    name='cloudmonitor',
    version='0.0.1',
    url='http://www.nokia-sbell.com',
    license='BSD',
    author='Nokia-sbell Chengdu SDN Team',
    author_email='xiaobo.chen@nokia-sbell.com',
    description='cloudmonitor',
    long_description=long_description,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[],
    classifiers=[
        'Programming Language :: Python :: 3.6'
    ],
    entry_points=entrypoints
)
