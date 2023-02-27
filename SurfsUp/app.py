import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

# Create Engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(autoload_with=engine)

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

# Start at the homepage and list all the available routes
@app.route("/")
def welcome():
    """Available api routes."""
    return (
        f"Available Routes: <br/>"
        f"/api/v1.0/precipitation <br/>"
        f"/api/v1.0/stations <br/>"
        f"/api/v1.0/tobs <br/>"
        f"/api/v1.0/start/<start_date> <br/>"
        f"/api/v1.0/start_end/<start_date>/<end_date> <br/>"
    )


# Convert the query results from your precipitation analysis and return the JSON representation of your dictionary
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Determine the most recent date
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    most_recent_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d')
    most_recent_date = most_recent_date.date()
    
    # Calculate the date one year from the last date in data set
    one_year_ago_date = last_date = most_recent_date - dt.timedelta(days = 365)

    # Perform a query to retrieve the data
    precip = session.query(Measurement.date, Measurement.prcp).where(Measurement.date >= last_date, Measurement.station >= one_year_ago_date).all()
    session.close()

    # Return the results jsonified
    precip_list = []
    for date, prcp in precip:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["prcp"] = prcp
        precip_list.append(precip_dict)

    return jsonify(precip_list)


# Return a JSON list of stations from the dataset
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Perform a query to retrieve the data
    stations = session.query(Station.station).all()
    
    session.close()

    # Return the results jsonified
    stations_list = list(np.ravel(stations))

    return jsonify(stations_list)


# Query the dates and temperature observations of the most-active station for the previous year of data
# and return a JSON list of temperature observations for the previous year
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Find the most recent date for the most-active station
    most_recent_date_mas = session.query(Measurement.date).filter(Measurement.station == 'USC00519281').order_by(Measurement.date.desc()).first()[0]
    most_recent_date_mas = dt.datetime.strptime(most_recent_date_mas, '%Y-%m-%d')
    most_recent_date_mas = most_recent_date_mas.date()


    # Calculate the date one year from the last date in data set
    one_year_previous_date_mas = most_recent_date_mas - dt.timedelta(days = 365)

    # Perform a query to retrieve the data
    mas_temps = session.query(Measurement.date, Measurement.tobs)\
        .filter(Measurement.station == 'USC00519281')\
            .where(Measurement.date >= one_year_previous_date_mas)\
                .order_by(Measurement.date).all()
    
    # Return the results jsonified
    mas_list = []
    for date, tobs in mas_temps:
        mas_dict = {}
        mas_dict["Date"] = date
        mas_dict["Tobs"] = tobs
        mas_list.append(mas_dict)

    return jsonify(mas_list)


# Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start date
@app.route("/api/v1.0/start/<start_date>")
def start(start_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Perform a query to retrieve the data
    query_result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
        .filter(Measurement.date >= start_date).all()
    
    session.close()

    # Return the results jsonified
    query_list = []
    for min,avg,max in query_result:
        query_dict = {}
        query_dict["Min"] = min
        query_dict["Average"] = avg
        query_dict["Max"] = max
        query_list.append(query_dict)

    return jsonify(query_list)


# Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start-end range
@app.route("/api/v1.0/start_end/<start_date>/<end_date>")
def start_end(start_date, end_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Perform a query to retrieve the data
    query_result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
        .filter(Measurement.date >= start_date)\
            .filter(Measurement.date <= end_date).all()
    
    session.close()

    # Return the results jsonified
    query_list = []
    for min,avg,max in query_result:
        query_dict = {}
        query_dict["Min"] = min
        query_dict["Average"] = avg
        query_dict["Max"] = max
        query_list.append(query_dict)

    return jsonify(query_list)


if __name__ == '__main__':
    app.run(debug=True)
