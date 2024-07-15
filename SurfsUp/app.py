# Import the dependencies.
import numpy as np

import sqlalchemy
import datetime as dt
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
measurementForHawaii = Base.classes.measurement
stationForHawaii = Base.classes.station

# Create our session (link) from Python to the DB


#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def getroutes():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
        f"Note: to access values between a start and end date enter both dates using format: YYYY-mm-dd/YYYY-mm-dd"
    )

# Convert the query results from your precipitation analysis
@app.route("/api/v1.0/precipitation")
def getprecipitation():
    session = Session(engine)
    presQueryResults = session.query(measurementForHawaii.prcp, measurementForHawaii.date).all()
    session.close()
    precQueryValues = []
    for prcp, date in presQueryResults:
        presDict = {}
        presDict["precipitation"] = prcp
        presDict["date"] = date
        precQueryValues.append(presDict)

    return jsonify(precQueryValues) 

# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def getstation(): 
    session = Session(engine)
    stationQueryRes = session.query(stationForHawaii.station,stationForHawaii.id).all()
    session.close()  
    
    stationsList = []
    for station, id in stationQueryRes:
        stationDict = {}
        stationDict['station'] = station
        stationDict['id'] = id
        stationsList.append(stationDict)
    return jsonify (stationsList) 

# Query the dates and temperature observations of the most-active station for the previous year of data.
# Return a JSON list of temperature observations for the previous year.
@app.route("/api/v1.0/tobs") 
def findTobs():
    session = Session(engine)
    lastYearQuery = session.query(measurementForHawaii.date).\
        order_by(measurementForHawaii.date.desc()).first() 
    print(lastYearQuery)
    lastYearQueryList = []
    for date in lastYearQuery:
        lastYearDict = {}
        lastYearDict["date"] = date
        lastYearQueryList.append(lastYearDict) 
    print(lastYearQueryList)
    query_start_date = dt.date(2017, 8, 23)-dt.timedelta(days =365) 
    print(query_start_date) 
    active_station= session.query(measurementForHawaii.station, func.count(measurementForHawaii.station)).\
        order_by(func.count(measurementForHawaii.station).desc()).\
        group_by(measurementForHawaii.station).first()
    most_active_station = active_station[0] 
    session.close() 
    print(most_active_station)
    dates_tobs_last_year_query_results = session.query(measurementForHawaii.date, measurementForHawaii.tobs, measurementForHawaii.station).\
        filter(measurementForHawaii.date > query_start_date).\
        filter(measurementForHawaii.station == most_active_station) 
    datesTobsList = []
    for date, tobs, station in dates_tobs_last_year_query_results:
        datesTobDict = {}
        datesTobDict["date"] = date
        datesTobDict["tobs"] = tobs
        datesTobDict["station"] = station
        datesTobsList.append(datesTobDict)
        
    return jsonify(datesTobsList) 

# Define function, set "start" date entered by user as parameter for start_date decorator 
@app.route("/api/v1.0/<start>")
def startDate(start):
    session = Session(engine) 
    startList = session.query(func.min(measurementForHawaii.tobs),func.avg(measurementForHawaii.tobs),func.max(measurementForHawaii.tobs)).\
        filter(measurementForHawaii.date >= start).all()
    session.close() 
    startDateList =[]
    for min, avg, max in startList:
        startTobDicts = {}
        startTobDicts["min"] = min
        startTobDicts["average"] = avg
        startTobDicts["max"] = max
        startDateList.append(startTobDicts)
    
    return jsonify(startDateList)


@app.route("/api/v1.0/<start>/<end>")
def start_and_end_date(start, end):
    session = Session(engine)
    startEndResultsList = session.query(func.min(measurementForHawaii.tobs), func.avg(measurementForHawaii.tobs), func.max(measurementForHawaii.tobs)).\
        filter(measurementForHawaii.date >= start).\
        filter(measurementForHawaii.date <= end).all()

    session.close()
  
    
    startList = []
    for min, avg, max in startEndResultsList:
        startEndTobsDict = {}
        startEndTobsDict["min_temp"] = min
        startEndTobsDict["avg_temp"] = avg
        startEndTobsDict["max_temp"] = max
        startList.append(startEndTobsDict) 
    

    return jsonify(startList)
   
if __name__ == '__main__':
    app.run(debug=True) 