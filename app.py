import numpy as np
import pandas as pd
import datetime as dt

# Python SQL toolkit and Object Relational Mapper
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
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date<br/>"                
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of precipitation by date"""
    # Query Measurement table 
    session = Session(engine)
    # Query Measurement table precipitation and date, and order by date
    results = session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date).all()  

    # Create a dictionary from the row data and append to a list of all_precipitation
    all_precipitation = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict[date] = prcp   
        all_precipitation.append(prcp_dict)

    return jsonify(all_precipitation)
    

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of all stations"""
    # Query Station Table
    session = Session(engine)
    # Query Station table 
    results = session.query(Station.station).all()  

    all_station = []
    for station in results:
        all_station.append(station)

    return jsonify(all_station)


@app.route("/api/v1.0/tobs")
def tobs():
    """Return Temperature Observations for the previous year"""
    # Query Measurement table
    session = Session(engine)
    # Query Measurement table temperature and date, and order by date
    results = session.query(Measurement.date, Measurement.tobs).order_by(Measurement.date).all()  

    # Save the query results as a Pandas DataFrame
    df = pd.DataFrame(results, columns=['Date', 'Temperature'])

    # Sort the dataframe by date
    df = df.sort_values('Date', ascending=False)

    # Convert the Date column from string to date object format  
    df['Date'] = pd.to_datetime(df['Date'])

    # Get the last 12 months of data   
    first_month = df.iloc[0,0]
    last_month = first_month - dt.timedelta(days=365)
    df_12m = df.loc[df['Date'] > last_month]
    df_12m['Date'] = df_12m['Date'].dt.strftime("%m/%d/%Y")
    all_temperature = df_12m.values.tolist() 
    return jsonify(all_temperature)

@app.route("/api/v1.0/<start_date>")
def start(start_date):
    """Return Temperature Observations for the previous year"""
    # Query Measurement table
    session = Session(engine)

    ret_list = []

    ret_list = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()    
    
    return jsonify(ret_list)    

@app.route("/api/v1.0/<start_date>/<end_date>")
def range(start_date, end_date):
    """Return Temperature Observations for the previous year"""
    # Query Measurement table
    session = Session(engine)

    ret_list = []

    ret_list = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()    
    
    return jsonify(ret_list)        


if __name__ == '__main__':
    app.run(debug=True)
