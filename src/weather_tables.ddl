-- Table to store weather station metadata
CREATE TABLE weather_station (
    station_id SERIAL PRIMARY KEY,
    station_code VARCHAR(20) UNIQUE NOT NULL,  
    state CHAR(2) NOT NULL,                    
    station_name VARCHAR(100)                  
);

-- Table to store daily weather data per station
CREATE TABLE weather_record (
    record_id SERIAL PRIMARY KEY,
    station_id INTEGER NOT NULL REFERENCES weather_station(station_id) ON DELETE CASCADE,
    record_date DATE NOT NULL,
    max_temp INTEGER,         
    min_temp INTEGER,         
    precipitation INTEGER,    

    CONSTRAINT unique_station_date UNIQUE (station_id, record_date)
);


-- Staging table to load raw data
CREATE TEMP TABLE weather_staging (
    station_code VARCHAR(20),
    record_date DATE,
    max_temp INTEGER,
    min_temp INTEGER,
    precipitation INTEGER
);

-- Logging table
CREATE TABLE weather_ingest_log (
    log_id SERIAL PRIMARY KEY,
    station_code VARCHAR(20),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    records_ingested INTEGER
);

