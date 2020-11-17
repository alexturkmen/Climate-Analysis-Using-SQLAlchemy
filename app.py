# Import necessary libraries
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify

# Create engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Create base
Base = automap_base()

# Connect base to engine
Base.prepare(engine, reflect=True)

# Create connection to measurement class
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create required routes
app = Flask(__name__)

@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate App API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/START_DATE<br/>"
        f"Please type your start date in YYYY-MM-DD format to retrieve min, avg and max of observed temperatures.<br/>"
        f"/api/v1.0/START_DATE/END_DATE<br/>"
        f"Please type your start date and end date in YYYY-MM-DD/YYYY-MM-DD format to retrieve min, avg and max of observed temperatures."
    )


@app.route("/api/v1.0/precipitation")
def prcp():
    #Create Session
    session = Session(engine)

    # Query results
   
    most_active_station = session.query(Station.station, Station.name, func.count(Measurement.tobs)).\
    filter(Measurement.station == Station.station).\
    group_by(Station.station).\
    order_by(func.count(Measurement.tobs).desc()).first()[0]

    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.station == most_active_station).all()

    session.close()

    date_prcp = []

    for date, prcp in results:
        prcp_dict = {}
        prcp_dict['Date'] = date
        prcp_dict['Precipitation'] = prcp
        date_prcp.append(prcp_dict)

    return jsonify(date_prcp)


@app.route("/api/v1.0/stations")
def stations():
    #Create Session
    session = Session(engine)

    # Query results
   
    results = session.query(Station.station).all()

    session.close()

    all_stations = list(np.ravel(results))

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    #Create Session
    session = Session(engine)

    # Query results
   
    most_active_station = session.query(Station.station, Station.name, func.count(Measurement.tobs)).\
    filter(Measurement.station == Station.station).\
    group_by(Station.station).\
    order_by(func.count(Measurement.tobs).desc()).first()[0]

    results = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.station == most_active_station).all()

    session.close()

    tobs_list = []

    for date, tobs in results:
        tobs_dict = {}
        tobs_dict['Temperature Observation (F)'] = tobs
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)


@app.route("/api/v1.0/<start>")
def start_date(start):
    #Create Session
    session = Session(engine)

    # Query results

    dates = session.query(Measurement.date).all()

    dates = list(np.ravel(dates))
    
    if start in dates:
        calc_start = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

        session.close()
   

        result = list(np.ravel(calc_start))

        result_dict = {'Min Temperature (F)': result[0], 'Avg Temperature (F)': result[1], 'Max Temperature (F)': result[2]}

        return jsonify(result_dict)
    else:
        return (f'Oops, we have encountered a problem!<br>'
                f'Possible Results:<br>'
                f'1. The date you search for is not within the data set.<br>'
                f'2. You have not typed the date in the required format.<br>'
                f'Note: Required Date Format is YYYY-MM-DD'
        )


@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    #Create Session
    session = Session(engine)

    # Query results

    dates = session.query(Measurement.date).all()

    dates = list(np.ravel(dates))
    
    if start in dates:
        if end in dates:

            calc_start = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).filter(Measurement.date <= end).all()

            session.close()
   
            result = list(np.ravel(calc_start))

            result_dict = {'Min Temperature (F)': result[0], 'Avg Temperature (F)': result[1], 'Max Temperature (F)': result[2]}

            return jsonify(result_dict)
        else:
            return (f'Oops, we have encountered a problem!<br>'
                    f'Possible Results:<br>'
                    f'1. The end date you search for is not within the data set.<br>'
                    f'2. You have not typed the end date in the required format.<br>'
                    f'Note: Required Date Format is YYYY-MM-DD'
            )

    return (f'Oops, we have encountered a problem!<br>'
            f'Possible Results:<br>'
            f'1. The start date you search for is not within the data set.<br>'
            f'2. You have not typed the start date in the required format.<br>'
            f'Note: Required Date Format is YYYY-MM-DD'
            )


if __name__ == "__main__":
    app.run(debug=True)