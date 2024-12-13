# Import the dependencies.
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
# NOTE: Done in each Flask route below, when necessary

session = Session(engine)
most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
session.close()

date_format = "%Y-%m-%d"

end_date_string = most_recent_date[0]
end_datetime = dt.datetime.strptime(end_date_string, date_format)
start_datetime = end_datetime - dt.timedelta(days=365)

start_date_last_12_months = start_datetime.strftime(date_format)
end_date_last_12_months = end_datetime.strftime(date_format)

def get_most_active_station():
    session = Session(engine)
    station_count = session.query(Station.station, func.count(Measurement.station)).\
                          filter(Measurement.station == Station.station).\
                          group_by(Station.station).order_by(func.count(Measurement.station).desc()).all()
    most_active_station = station_count[0][0]
    session.close()
    return most_active_station

def get_observations_by_date(observation_fields, start_date, end_date, most_active=False):
    selection = [Measurement.date, observation_fields]

    session = Session(engine)
    if most_active:
        last_year_query = session.query(*selection).filter(Measurement.date>=start_date).\
                filter(Measurement.date<=end_date).\
                filter(Measurement.station==get_most_active_station()).all()
    else:
        last_year_query = session.query(*selection).filter(Measurement.date>=start_date).filter(Measurement.date<=end_date).all()
    session.close()

    return jsonify(dict(last_year_query))

# Retrieve the minimum, average, and maximum tempteratures between a given start date and end date
def get_statistics_by_date(start_date, end_date):
    selection = [func.min(Measurement.tobs),
                 func.avg(Measurement.tobs),
                 func.max(Measurement.tobs)]
    
    session = Session(engine)
    last_year_query = session.query(*selection).\
            filter(Measurement.date>=start_date).\
            filter(Measurement.date<=end_date).all()
    session.close()

    stats = {}

    stats['date_start'] = start_date
    stats['date_end'] = end_date
    stats['min'] = last_year_query[0][0]
    stats['avg'] = last_year_query[0][1]
    stats['max'] = last_year_query[0][2]

    return jsonify(stats)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    # List all the available routes
    return (f"""
        <h1>Climate API for Honolulu, HI</h1>
        <h3>Using this API you can retrieve the following information:</h3>
        <ul>
        <li>Last 12 months of precipitation observations from all stations<br/>
            <a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a>
        </li><br/>
        <li>Station information for all stations<br/>
            <a href='/api/v1.0/stations'>/api/v1.0/stations</a>
        </li><br/>
        <li>Last 12 months of temperature observations for the most active station ({get_most_active_station()})<br/>
            <a href='/api/v1.0/tobs'>/api/v1.0/tobs</a>
        </li><br/>
        <li>Minimum, average, and maximum temperature beginning from a start date<br/>
            <a href='/api/v1.0/<start>'>/api/v1.0/&lt;start&gt;<a/>
        </li><br/>
        <li>Minimum, average, and maximum temperature beginning from a start date to an end date<br/>
            <a href='/api/v1.0/<start>/<end>'>/api/v1.0/&lt;start&gt;/&lt;end&gt;</a>
        </li><br/>
        <b>Note:</b> &lt;start&gt; and &lt;end&gt; dates should be in format of YYYY-MM-DD (no angle brackets)<br/>
        Dated links must be edited manually to correctly retrieve data.        
        </ul>
        

        """
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Convert the query results from your precipitation analysis 
    # (i.e. retrieve only the last 12 months of data) to a 
    # dictionary using date as the key and prcp as the value.
    # Return the JSON representation of your dictionary
    return (get_observations_by_date(Measurement.prcp,
                                     start_date_last_12_months,
                                     end_date_last_12_months))

@app.route("/api/v1.0/stations")
def stations():
    # Return a JSON list of stations from the dataset
    session = Session(engine)
    results = session.query(Station.name).all()
    session.close()

    stations = list(np.ravel(results))

    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def temp():
    # Return a JSON list of temperature observations for the previous year
    return (get_observations_by_date(Measurement.tobs,
                                     start_date_last_12_months,
                                     end_date_last_12_months,
                                     True))

@app.route("/api/v1.0/<start>")
def date_start(start):
    # Return a JSON list of the minimum temperature, the average temperature,
    # and the maximum temperature for a specified start
    
    return (get_statistics_by_date(start,
                                   end_date_last_12_months))

@app.route("/api/v1.0/<start>/<end>")
def date_start_end(start, end):
    # Return a JSON list of the minimum temperature, the average temperature,
    # and the maximum temperature for a specified start-end range
    return (get_statistics_by_date(start,
                                   end))

if __name__ == '__main__':
    app.run(debug=True)