# import dependency
import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# Set up the Database for query
# ProgrammingERROR in tobs and temps route 
    #SQLite objects created in a thread can only be used in that same thread
    #added   connect_args = {"check_same_thread": False})
    # THanks Joshua Katz
# reflect that database into classes
engine = create_engine("sqlite:///hawaii.sqlite", connect_args = {"check_same_thread": False})
# reflect that database into classes
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

#link Python to database 
session = Session(engine)

# create new "app Instance" 
# # NOTICE double underscore before and after! This is Magic Methods in Python
## "instance" general term for singular version of something
app = Flask(__name__)

# Create Flask Route 
# Define starting point... AKA... ROOT . use function @app.route('/')
# / indicated we want to put our data at the root of our routes
    # commonly known as highest level of hierarchy in any computer system
# Create function "hello_world"
    # when creating put code for that specific route below @app.route()

#Root route
@app.route("/")
def welcome():
    return(
    '''
    Welcome to the Climate Analysis API!<br/>
    Available Routes:<br/>
    /api/v1.0/precipitation<br/>
    /api/v1.0/stations<br/>
    /api/v1.0/tobs<br/>
    /api/v1.0/temp/start/end
    ''')

#create the precipitation function
# calculate date one year ago from today
# query date and precipitation for previous year
# create dictionary with date as key and precip as value Jsonify()
@app.route("/api/v1.0/precipitation")
def precipitation():
    prev_year = dt.date(2017, 8, 23) -dt.timedelta(days=365)
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)

# create route to return a list of all the weather stations
# use np.ravel() function with results to unravel results in one-dimensional array.
@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()
    stations = list(np.ravel(results))
    return jsonify(stations=stations)

# create route to return temp of previous year
@app.route("/api/v1.0/tobs")
def temp_monthly():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

# Create route for min, avg, max temps with start and end date
# add start and end parameters to stats set to NONE
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        results = session.qyery(*sel).\
            filter(Measurement.date >= start).all()
        temps = list(np.ravel(results))
        return jsonify(temps=temps)

    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps)

if __name__ == '__main__':
    app.run(debug=True)
