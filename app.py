# Import the dependencies.
import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


#################################################
# Database Setup
#################################################
# Connect to engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# Reflect an existing database into a new model
Base = automap_base()
   
# Reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
# Shaun - instructor said to remove this code
##session = Session(engine)

#measurement table
##measurement_results = session.query(Measurement.station, Measurement.date, Measurement.prcp, Measurement.tobs).all()

#station table
##station_results = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()


#################################################
# Flask Setup
#################################################
from flask import Flask, jsonify

# Create app from flask
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
# Define routes

# Create list of available links
@app.route('/')
def home():
    return("""
    Available routes:<br/>
    - /api/v1.0/precipitation<br/>
    - /api/v1.0/stations<br/>
    - /api.v1.0/tobs<br/>
    - /api.v1.0/<start><br/>
    - /api/v1.0/<start>/<end> 
    """          
    )

# Preceipitation dictionary
@app.route("/api/v1.0/precipitation")
def precipitation():
# Create session
    session = Session(engine)
        
# Calculate date from most recent
    one_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

# Obtain 12 months
    results = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= one_year).all()

# Create dictionary to pull data
    precipitation_data = {}
    for date, prcp in results:
        precipitation_data[date] = prcp

    session.close()

    return jsonify(precipitation_data)

# Create list of stations
@app.route("/api/v1.0/stations")
def stations():
    # Create a session
    session = Session(engine)
    
    # Query the station names
    results = session.query(Station.station, Station.name).all()
    
    # Convert the results to dictionaries
    station_list = []
    for station, name in results:
        station_dict = {}
        station_dict['station'] = station
        station_dict['name'] = name
        station_list.append(station_dict)
    
    session.close()
    
    return jsonify(station_list)

# Create list of tobs
@app.route("/api/v1.0/tobs")
def tobs():
    # Create a session
    session = Session(engine)
    
    # Query the most active station
    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count().desc()).\
        first()
    
    # Calculate the date one year ago from the last date 
    last_date = session.query(Measurement.date).\
        order_by(Measurement.date.desc()).\
        first()
    one_year_ago = dt.datetime.strptime(last_date[0], '%Y-%m-%d') - dt.timedelta(days=365)
    
    # Obtain the temperature observations from previous year
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station[0]).\
        filter(Measurement.date >= one_year_ago).\
        all()
    
       
    # Create dictionaries with date and temperature
    tobs_list = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict['date'] = date
        tobs_dict['tobs'] = tobs
        tobs_list.append(tobs_dict)

    
    session.close()    
    
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def calc_temps_start(start):
    
    # Create a session
    session = Session(engine)
    
    # Query the min, ave, and max temps for dates greater/equal of start date
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        all()
    
    # Create a dictionary of temp values
    temps_dict = {
        'TMIN': results[0][0],
        'TAVG': results[0][1],
        'TMAX': results[0][2]
    }
   
    session.close()

    return jsonify(temps_dict)

# Create End s
@app.route("/api/v1.0/<start>/<end>")
def calc_temps_start_end(start, end):
    
    session = Session(engine)
    
    # Query the min, ave, max temps on dates between start/end
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).\
        all()
    
    # Create a dictionary of temp values
    temps_dict = {
        'TMIN': results[0][0],
        'TAVG': results[0][1],
        'TMAX': results[0][2]
    }

    session.close()
    
    return jsonify(temps_dict)

## Run development server
if __name__ == '__main__':
    app.run(debug=True)