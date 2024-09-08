# Import the dependencies.
import numpy as np
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, cast, Date, text
from sqlalchemy.dialects import sqlite
from flask import Flask, jsonify

# To run or Debug in VSCode
import os
os.chdir(os.path.dirname(__file__))


#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return (
        f"Aloha to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end<br/>"
        f"<p>'start' and 'end' date should be in the format MMDDYYYY.</p>"

    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data for one year ago"""
    # Calculate the date one year from the last date in data set.
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()

    session.close()
    # Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
    precipitation = {date: prcp for date, prcp in precipitation_data}
    # Return the results
    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations"""
    results = session.query(Station.station).all()

    session.close()

    # Convert list into normal list
    stations_list = list(np.ravel(results))
    # Return the results
    return jsonify(stations_list=stations_list) 

@app.route("/api/v1.0/tobs")
def tobs():
    """Return the temperature observations (tobs) for one year ago"""
    # Calculate the date one year from the last date in data set.
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query the dates and temperature observations of the most active station for the last year of data.
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= one_year_ago).all()

    session.close()
    # Convert the query results to a list
    tobs_list = list(np.ravel(results))
    # Return the results
    return jsonify(tobs_list=tobs_list)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    """Return the minimum temperature, the average temperature, and the max temperature for a given date range"""
    # Query to select the minimum, average, and maximum temperatures from the SQLite database
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        # Calculate TMIN, TAVG, and TMAX for dates greater than and equal to the start date
        start = dt.datetime.strptime(start, '%m%d%Y').strftime('%Y-%m-%d')
        results = session.query(*sel).filter(Measurement.date >= start).all()
        session.close()
        # Convert the query results to a list
        temps = list(np.ravel(results))
        # Return the results
        return jsonify(temps)
    # Calculate the minimum, average, and maximum temperatures for the date range
    start = dt.datetime.strptime(start, '%m%d%Y').strftime('%Y-%m-%d')
    end = dt.datetime.strptime(end, '%m%d%Y').strftime('%Y-%m-%d')

    # Calculate TMIN, TAVG, and TMAX with start and end dates.
    sql = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end)
    results = sql.all()

    sql_string = str(sql.statement.compile(dialect=sqlite.dialect()))

    # Structure table
    table_name = '"Temperature Measurements"'
    result = session.execute(text(f"PRAGMA table_info({table_name});")).all()
    info = list(np.ravel(result))
    print(list)
    print(info)

    session.close()

    # Convert the query results to a list
    mytemps = {
        "temps": list(np.ravel(results)),
    }

    # Return the results
    return jsonify(temps=mytemps)

if __name__ == '__main__':
    app.run(debug=True)