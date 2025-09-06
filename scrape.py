#!/usr/bin/env python3
"""
Amtrak Moynihan Train Hall Scraper

This script scrapes train schedule data from the Moynihan Train Hall website
and stores it in a SQLite database. All datetime operations use the timezone
specified by the TZ environment variable (defaults to America/New_York).
"""

import datetime
import primp
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List
import argparse
import sqlite3
import os
import pytz

# Get timezone from environment variable, default to America/New_York
TIMEZONE_NAME = os.environ.get('TZ', 'America/New_York')
TIMEZONE = pytz.timezone(TIMEZONE_NAME)


@dataclass
class Train:
    day: str
    time: str
    train_number: str
    train_name: str
    destination: str
    status: str
    track: str = ""

@dataclass
class ScheduleBoard:
    departures: List[Train]
    arrivals: List[Train]

def adapt_date_iso(val):
    """Adapt datetime.date to ISO 8601 date."""
    return val.isoformat()

def adapt_datetime_iso(val):
    """Adapt datetime.datetime to timezone-aware ISO 8601 date."""
    if val.tzinfo is None:
        # If naive datetime, assume it's in the configured timezone
        val = TIMEZONE.localize(val)
    return val.isoformat()

def adapt_datetime_epoch(val):
    """Adapt datetime.datetime to Unix timestamp."""
    return int(val.timestamp())

sqlite3.register_adapter(datetime.date, adapt_date_iso)
sqlite3.register_adapter(datetime.datetime, adapt_datetime_iso)
sqlite3.register_adapter(datetime.datetime, adapt_datetime_epoch)

def convert_date(val):
    """Convert ISO 8601 date to datetime.date object."""
    return datetime.date.fromisoformat(val.decode())

def convert_datetime(val):
    """Convert ISO 8601 datetime to datetime.datetime object."""
    dt = datetime.datetime.fromisoformat(val.decode())
    if dt.tzinfo is None:
        # If naive datetime, assume it's in the configured timezone
        dt = TIMEZONE.localize(dt)
    return dt

def convert_timestamp(val):
    """Convert Unix epoch timestamp to datetime.datetime object."""
    dt = datetime.datetime.fromtimestamp(int(val))
    if dt.tzinfo is None:
        # If naive datetime, assume it's in the configured timezone
        dt = TIMEZONE.localize(dt)
    return dt

sqlite3.register_converter("date", convert_date)
sqlite3.register_converter("datetime", convert_datetime)
sqlite3.register_converter("timestamp", convert_timestamp)

def init_database(db_path: str):
    """Initialize the SQLite database with the train_track_locations table."""
    conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS train_track_locations (
            day DATE,
            time DATETIME,
            schedule_time TEXT,
            train_number TEXT,
            train_name TEXT,
            destination TEXT,
            status TEXT,
            track TEXT,
            PRIMARY KEY (day, time, train_number)
        )
    ''')
    
    conn.commit()
    conn.close()

def upsert_train_data(trains: List[Train], db_path: str):
    """Upsert train data into the database."""
    conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    
    for train in trains:
        # Convert day string to DATE and time string to DATETIME
        # Assuming day is in YYYY-MM-DD format and time is in HH:MM format
        try:
            day_date = datetime.datetime.strptime(train.day, "%Y-%m-%d").date()
            # Combine day and time to create a full datetime in the configured timezone
            naive_datetime = datetime.datetime.strptime(f"{train.day} {train.time}", "%Y-%m-%d %H:%M %p")
            time_datetime = TIMEZONE.localize(naive_datetime)
        except ValueError as e:
            print(f"Warning: Could not parse date/time for train {train.train_number}: {e}")
            continue
            
        cursor.execute('''
            INSERT OR REPLACE INTO train_track_locations 
            (day, time, schedule_time, train_number, train_name, destination, status, track)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            day_date,
            time_datetime,
            train.time,
            train.train_number,
            train.train_name,
            train.destination,
            train.status,
            train.track
        ))
    
    conn.commit()
    conn.close()


def parse(data):
    soup = BeautifulSoup(data, 'html.parser')
    trains = []
    
    # Find all train header rows
    header_rows = soup.find_all('tr', class_='amtrak-header-row')

    if not header_rows:
        print(f"No header rows found: {soup=}")
    
    for header_row in header_rows:
        # Extract time from the first td
        time_cell = header_row.find('td')
        time = time_cell.get_text(strip=True) if time_cell else ""
        
        # Extract train number and name from the second td
        train_cell = header_row.find_all('td')[1] if len(header_row.find_all('td')) > 1 else None
        train_number = ""
        train_name = ""
        
        if train_cell:
            train_number_span = train_cell.find('span', class_='train-number')
            train_name_span = train_cell.find('span', class_='train-name')
            
            train_number = train_number_span.get_text(strip=True) if train_number_span else ""
            train_name = train_name_span.get_text(strip=True) if train_name_span else ""
        
        # Find the corresponding destination row (next sibling)
        destination_row = header_row.find_next_sibling('tr', class_='amtrak-destination')
        
        destination = ""
        status = ""
        track = ""
        
        if destination_row:
            # Extract destination and status from pill-cell
            pill_cell = destination_row.find('td', class_='pill-cell')
            if pill_cell:
                destination_span = pill_cell.find('span', class_='pill-destination')
                status_span = pill_cell.find('span', class_='pill-status')
                
                destination = destination_span.get_text(strip=True) if destination_span else ""
                status = status_span.get_text(strip=True) if status_span else ""
            
            # Extract track from track-cell
            track_cell = destination_row.find('td', class_='track-cell')
            track = track_cell.get_text(strip=True) if track_cell else ""
        
        # Create Train object and add to list
        train = Train(
            day=datetime.datetime.now(TIMEZONE).strftime("%Y-%m-%d"),
            time=time,
            train_number=train_number,
            train_name=train_name,
            destination=destination,
            status=status,
            track=track
        )
        print(f"Found train: {train=}")
        trains.append(train)
    
    return trains


def scrape():
    r = primp.get('https://moynihantrainhall.nyc/transportation/', headers={'Referer': 'https://moynihantrainhall.nyc/'})
    if r.status_code != 200:
        raise Exception(f"Failed to scrape: {r.status_code}: {r.text}")
    
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Find the tables and convert to string for parsing
    departures_table = soup.find(id='amtrak-departures-target')
    arrivals_table = soup.find(id='amtrak-arrivals-target')
    
    return ScheduleBoard(
        departures=parse(str(departures_table) if departures_table else ""),
        arrivals=parse(str(arrivals_table) if arrivals_table else ""),
    )

def find_trains_with_tracks(schedule_board: ScheduleBoard):
    """Find all trains that have track information."""
    trains = []
    # Combine departures and arrivals, filter for trains with tracks
    all_trains = schedule_board.departures + schedule_board.arrivals
    for train in all_trains:
        if train.track:
            trains.append(train)
    return trains


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scrape Amtrak train data from Moynihan Train Hall')
    parser.add_argument('--db', default='train_data.sqlite3', help='Path to SQLite database file')
    args = parser.parse_args()
    
    # Initialize database
    init_database(args.db)
    
    # Scrape data
    schedule_board = scrape()
    
    # Find trains with tracks
    trains_with_tracks = find_trains_with_tracks(schedule_board)

    print(f'{trains_with_tracks=}')
    
    # Upsert data into database
    upsert_train_data(trains_with_tracks, args.db)
    
    print(f"Successfully stored {len(trains_with_tracks)} trains with track information in database: {args.db}")