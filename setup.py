from setuptools import setup

requirements = []
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

readme = ''
with open('README.md') as f:
    readme = f.read()

setup(
    name='jackson-bot',
    version='0.0.1',
    author='benjaminchang23',
    description='A discord bot for managing jackson street operations',
    long_description=readme,
    packages=setuptools.find_packages(),
    install_requires=requirements,

    entry_points={
        'console_scripts': [
            'jackson-bot=jackson-bot.launcher:main',
        ],
    },

    scripts=[
    ]
)
