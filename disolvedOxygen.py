from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
import pytz
import uvicorn

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
@app.get("/table", response_class=HTMLResponse)
async def get_table():
        return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sensor Data</title>
        <style>
            table {
                width: 100%;
                border-collapse: collapse;
            }
            th, td {
                border: 1px solid black;
                padding: 8px;
                text-align: left;
            }
            th {
                background-color: #f2f2f2;
            }
        </style>
    </head>
    <body>
        <h1>Sensor Data</h1>
        <table id="sensorTable">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Temperature</th>
                    <th>DO Concentration</th>
                    <th>Time</th>
                </tr>
            </thead>
            <tbody>
                <!-- Data will be inserted here by JavaScript -->
            </tbody>
        </table>
        <script>
            async function fetchSensorData() {
                const response = await fetch('/sensor-data/');
                const data = await response.json();
                
                const tableBody = document.getElementById('sensorTable').getElementsByTagName('tbody')[0];
                tableBody.innerHTML = ''; // Clear any existing rows
                
                data.forEach(row => {
                    const tr = document.createElement('tr');
                    
                    tr.innerHTML = `
                        <td>${row.id}</td>
                        <td>${row.temperature}</td>
                        <td>${row.do_concentration}</td>
                        <td>${row.time}</td>
                    `;
                    
                    tableBody.appendChild(tr);
                });
            }
            
            // Fetch data when the page loads
            window.onload = fetchSensorData;
        </script>
    </body>
    </html>
    """
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8081)
