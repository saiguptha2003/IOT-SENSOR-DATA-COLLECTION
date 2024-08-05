from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

app = FastAPI()

# Define the SQLite URL and create the database engine
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Create a base class for the declarative class definitions
Base = declarative_base()

# Create a session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define the Temperature table
class Temperature(Base):
    __tablename__ = "temperatures"
    id = Column(Integer, primary_key=True, index=True)
    temperature = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False)

# Create the tables in the database
Base.metadata.create_all(bind=engine)

# Model to define the data structure
class TemperatureData(BaseModel):
    temperature: float
    timestamp: datetime = None

# In-memory storage for collected data
data_storage: List[TemperatureData] = []

@app.post("/collect-data/")
async def collect_data(data: TemperatureData):
    # Ensure the timestamp is set to the current time if not provided
    if not data.timestamp:
        data.timestamp = datetime.now()

    # Create a new database session
    db = SessionLocal()
    # Add the new temperature data to the database
    new_temperature = Temperature(
        temperature=data.temperature,
        timestamp=data.timestamp
    )
    db.add(new_temperature)
    db.commit()
    db.refresh(new_temperature)
    db.close()

    # Also append to in-memory storage for demonstration
    data_storage.append(data)
    return {"message": "Data received successfully", "data": data}

@app.get("/data/")
async def get_data():
    # Create a new database session
    db = SessionLocal()
    # Query all temperature data from the database
    temperatures = db.query(Temperature).all()
    db.close()
    
    # Format the timestamp to a readable format
    formatted_temperatures = [
        {"id": temp.id, "temperature": temp.temperature, "timestamp": temp.timestamp.strftime("%Y-%m-%d %H:%M:%S")}
        for temp in temperatures
    ]
    return formatted_temperatures

# Example route to check if the server is running
@app.get("/")
async def read_root():
    return {"message": "FastAPI IoT data collection server is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
