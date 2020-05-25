from setuptools import setup

requirements = ["Click==7.0",
                "Fiona>=1.8.13",
                "geopandas==0.7.0",
                "networkx==2.3",
                "numpy==1.16.4",
                "pandas==0.25.0",
                "PyYAML==5.1.1",
                "requests==2.23.0",
                "scipy==1.4.1",
                "Shapely==1.7.0"]

setup(
    name="geobasenrn",
    version="0.1",

    # Project relies on scientific python and geospatial dependencies
    install_requires=requirements,

    # Need to include data and configuration files
    package_data={
        "geobasenrn": ["*.gpkg", "*.yaml"]
    },

    author="Statistics Canada",
    author_email="me@example.com",
    description="National Road Network - GeoBase series processing.",
    keywords="",
    url="https://open.canada.ca/data/en/dataset/3d282116-e556-400c-9306-ca1a3cada77f",
    project_urls={
        "Bug Tracker": "https://github.com/goatsweater/nrn-rrn/issues",
        "Documentation": "https://nrn-rrn.readthedocs.org",
        "Source Code": "https://github.com/goatsweater/nrn-rrn",
    },

    packages=['geobasenrn', 'geobasenrn.nrn'],
    entry_points='''
        [console_scripts]
        nrn=geobasenrn.nrn.main:main_group
        [geobasenrn.nrn_commands]
        package=geobasenrn.nrn.package:package
        validate=geobasenrn.nrn.validate:validate
        ls=geobasenrn.nrn.ls:ls
        convert=geobasenrn.nrn.convert:convert
        ''',
    classifiers=[
        "License :: OSI Approved :: MIT License"
    ]
)
