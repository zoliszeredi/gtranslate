import setuptools


setuptools.setup(
    name='scaraotschi',
    version='0.1.0',
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    install_requires=[
        'googletrans',
        'amqp',
        'python-daemon',
    ],
    entry_points={
        'console_scripts': [
            'gtd = scaraotschi.gtd:main',
            'gtranslate = scaraotschi.gtranslate:main',
        ]
    },
    license='MIT',
)
