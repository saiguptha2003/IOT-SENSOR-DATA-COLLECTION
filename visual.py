from fastapi import FastAPI,Request
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
import pytz
import uvicorn
from fastapi.staticfiles import StaticFiles
from jinja2 import Template
from fastapi.responses import HTMLResponse
import pandas as pd
app = FastAPI()

SQLALCHEMY_DATABASE_URL = "sqlite:///./data.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class SensorData(Base):
    __tablename__ = "sensor_data"
    id = Column(Integer, primary_key=True, index=True)
    temperature = Column(Float, nullable=False)
    do_concentration = Column(Float, nullable=False)
    time = Column(DateTime, nullable=False)

Base.metadata.create_all(bind=engine)

class SensorDataModel(BaseModel):
    temperature: float
    do_concentration: float
    time: datetime = None

@app.post("/collect-sensor-data/")
async def collect_sensor_data(data: SensorDataModel):
    if not data.time:
        tz = pytz.timezone('Asia/Kolkata')
        data.time = datetime.now(tz)
    
    db = SessionLocal()
    new_data = SensorData(
        temperature=data.temperature,
        do_concentration=data.do_concentration,
        time=data.time
    )
    db.add(new_data)
    db.commit()
    db.refresh(new_data)
    db.close()

    return {"message": "Data received successfully", "data": data}

@app.get("/sensor-data/")
async def get_sensor_data():
    db = SessionLocal()
    sensor_data = db.query(SensorData).all()
    db.close()
    
    formatted_data = [
        {"id": data.id, "temperature": data.temperature, "do_concentration": data.do_concentration, 
         "time": data.time.astimezone(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S")}
        for data in sensor_data
    ]
    return formatted_data

@app.get("/")
async def read_root():
    return {"message": "FastAPI sensor data collection server is running"}
@app.get("/graphs", response_class=HTMLResponse)
async def get_graphs(request: Request):
    db = SessionLocal()
    sensor_data = db.query(SensorData).all()
    db.close()

    if not sensor_data:
        return HTMLResponse(content="<h1>No data available</h1>", status_code=404)

    # Convert data to DataFrame
    df = pd.DataFrame([
        {"time": data.time, "temperature": data.temperature, "do_concentration": data.do_concentration}
        for data in sensor_data
    ])

    # Convert DataFrame to JSON
    data_json = df.to_dict(orient='records')

    # Load the HTML template
    with open('static/graphs.jinja2') as file:
        template_str = file.read()

    # Render template with data
    template = Template(template_str)
    html_content = template.render(data_json=data_json)
    return HTMLResponse(content=html_content)

# Serve static files from the 'static' directory
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8081)
