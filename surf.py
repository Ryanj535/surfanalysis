from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
import datetime as dt

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)

Base.classes.keys()

Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

last_date = session.query(func.max(Measurement.date)).all()
last_date_dt = dt.datetime.strptime(last_date[0][0], "%Y-%m-%d")
first_date = last_date_dt - dt.timedelta(days=365)

precipitation_data = session.query(Measurement.station, Measurement.date, Measurement.prcp).filter(Measurement.date >= first_date).all()

station_list = session.query(Measurement.station).distinct()

station_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date > first_date).filter(Measurement.station == "USC00519281").all()



app = Flask(__name__)

@app.route("/")
def Home():
    return (
    f"Welcome to the Home Page of My Climate App!<br/>"
    f"Please select from the following routes:<br/>"
    f"/api/v1.0/precipitation<br/>"
    f"/api/v1.0/stations<br/>"
    f"/api/v1.0/tobs<br/>"
    f"/api/v1.0/<start><br/>"
    f"/api/v1.0/<start>/<end>")

@app.route("/api/v1.0/precipitation")
def precipitation():
    prcp_data = []
    for station, date, prcp in precipitation_data:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["prcp"] = prcp
        prcp_data.append(precip_dict)
    return jsonify(prcp_data)

@app.route("/api/v1.0/stations")
def station():
    session=Session(engine)
    station_list = session.query(Measurement.station).distinct()
    station_list2 = []
    for x in station_list:
        station_dict = {}
        station_dict["Station"] = x
        station_list2.append(station_dict)
    return jsonify(station_list2)

@app.route("/api/v1.0/tobs")
def tobs():
    session=Session(engine)
    tobs = []
    for date, tob in station_data:
        tob_dict = {}
        tob_dict["date"] = date
        tob_dict["tobs"] = tob
        tobs.append(tob_dict)
    return jsonify(tobs)

@app.route("/api/v1.0/<start>")
def tob_start(start):
    session=Session(engine)
    start_tobs=[]
    tob_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    for min_temp, ave_temp, max_temp in tob_results:
        tob_ave_dict = {}
        tob_ave_dict["Tmin"] = min_temp
        tob_ave_dict["Tavg"] = ave_temp
        tob_ave_dict["Tmax"] = max_temp
        start_tobs.append(tob_ave_dict)
    return jsonify(start_tobs)

@app.route("/api/v1.0/<start>/<end>")
def tob_start_end(start, end):
    session=Session(engine)
    start_end_tobs=[]
    tob_results2 = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    for min_temp, ave_temp, max_temp in tob_results2:
        tob_temp_dict = {}
        tob_temp_dict["Tmin"] = min_temp
        tob_temp_dict["Tavg"] = ave_temp
        tob_temp_dict["Tmax"] = max_temp
        start_end_tobs.append(tob_temp_dict)
    return jsonify(start_end_tobs)

if __name__ == "__main__":
    app.run(debug=True)
