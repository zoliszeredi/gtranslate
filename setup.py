import setuptools


setuptools.setup(
    name='scaraotschi',
    version='0.1.0',
    author='Szeredi Tibor Zoltan',
    author_email='zoltan@szeredi.ro',
    description='cli google translate tool',
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
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    license='MIT',
)
