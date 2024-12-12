# Module_10_Challenge : *SQLAlchemy Challenge*

This repository contains an SQLite database and Python files to interact with it, relating to data from climate stations around Honolulu, Hawaii. The Jupyter Notebook climate.ipynb uses SQLAlchemy to conduct exploratory analysis of precipitation for all stations as well as temperature for the most active station. App.py serves a web site via Flask to provide API access to the database to retrieve data in JSON format reflecting these same exploratory analyses.

### Relevant Files

Python:

+ app.py *(Flask server to provide API access to the database)*
+ climate.ipynb *(Jupyter Notebook for analysis and data visualizations)*

Data:
+ Resources/hawaii.sqlite *(Database of climate stations and time series data of measurements in Honolulu, HI)*
+ Resources/hawaii_measurements.csv *(Measurements CSV file to populate database)*
+ Resources/hawaii_stations.csv *(Station data CSV file to populate database)*
