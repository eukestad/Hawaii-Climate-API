import numpy as np
import pandas as pd
import datetime as dt

from datetime import datetime, timedelta
from dateutil.relativedelta import *

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f'<a href="/api/v1.0/precipitation">/api/v1.0/precipitation</a><br/>'
        f'<a href="/api/v1.0/stations">/api/v1.0/stations</a><br/>'
        f'<a href="/api/v1.0/tobs">/api/v1.0/tobs</a><br/>'
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Find the most recent date in the data set.
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    lastdate_df = pd.DataFrame(most_recent_date, columns=['date'])

    lastdate = lastdate_df.to_string()[-10:]

    # Design a query to retrieve the last 12 months of precipitation data and plot the results. 
    # Starting from the most recent data point in the database. 
    lastdate_dt = datetime.strptime(lastdate,'%Y-%m-%d')

    # Calculate the date one year from the last date in data set.
    one_year_prev = lastdate_dt + relativedelta(months=-12)
    filterdate = one_year_prev.strftime('%Y-%m-%d')

    # Perform a query to retrieve the data and precipitation scores
    last12mnth_prcp = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date>=filterdate).all()
    session.close()

    """Convert the query results to a dictionary using date as the key and prcp as the value."""
    prcp_dates = {}

    for date, prcp in last12mnth_prcp:
        prcp_dates[date] = prcp

    """Return the JSON representation of your dictionary."""
    return jsonify(prcp_dates)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Return a JSON list of stations from the dataset.
    results = session.query(Station.station).all()

    session.close()

    stations = list(np.ravel(results))

    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs(): 
    # Create our session (link) from Python to the DB
    session = Session(engine)    

    # Query the dates and temperature observations of the most active station for the last year of data.
    # Find the most recent date in the data set.
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    lastdate_df = pd.DataFrame(most_recent_date, columns=['date'])

    lastdate = lastdate_df.to_string()[-10:]

    # Starting from the most recent data point in the database. 
    lastdate_dt = datetime.strptime(lastdate,'%Y-%m-%d')

    # Calculate the date one year from the last date in data set.
    one_year_prev = lastdate_dt + relativedelta(months=-12)
    filterdate = one_year_prev.strftime('%Y-%m-%d')

    active_stations = session.query(Measurement.station, func.count(Measurement.id)).group_by(Measurement.station)

    active_stations_df = pd.DataFrame(active_stations, columns=['station','observations']).sort_values(by='observations', ascending=False)

    mostactive = active_stations_df.head(1).iloc[0]['station']
    # Query the dates and temperature observations of the most active station
    last12mnth_temp = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date>=filterdate).filter(Measurement.station==mostactive).all()

    # Return a JSON list of temperature observations (TOBS) for the previous year.
    return jsonify(last12mnth_temp)

# @app.route("/api/v1.0/<start>")
# @app.route("/api/v1.0/<start>/<end>")
# def datefilter():
#     # Create our session (link) from Python to the DB
#     session = Session(engine)    
#     # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.

#     # When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.

#     # When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.  

# https://koenwoortman.com/python-flask-multiple-routes-for-one-function/#:~:text=In%20some%20cases%20you%20can,route%20decorator%20to%20the%20function.

if __name__ == '__main__':
    app.run(debug=True)