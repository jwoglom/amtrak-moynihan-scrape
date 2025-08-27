#!/usr/bin/env python3

from datetime import datetime
import primp
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List
import argparse


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

def parse(data):
    soup = BeautifulSoup(data, 'html.parser')
    trains = []
    
    # Find all train header rows
    header_rows = soup.find_all('tr', class_='amtrak-header-row')
    
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
            day=datetime.now().strftime("%Y-%m-%d"),
            time=time,
            train_number=train_number,
            train_name=train_name,
            destination=destination,
            status=status,
            track=track
        )
        trains.append(train)
    
    return trains


def scrape():
    r = primp.get('https://moynihantrainhall.nyc/transportation/', headers={'Referer': 'https://moynihantrainhall.nyc/'})
    if r.status_code != 200:
        raise Exception(f"Failed to scrape: {r.status_code}: {r.text}")
    
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Find the tables and convert to string for parsing
    departures_table = soup.find('table', id='amtrak-departures-target')
    arrivals_table = soup.find('table', id='amtrak-arrivals-target')
    
    return ScheduleBoard(
        departures=parse(str(departures_table) if departures_table else ""),
        arrivals=parse(str(arrivals_table) if arrivals_table else ""),
    )

def filter_with_tracks(schedule_board: ScheduleBoard):
    trains = []
    for train in zip(schedule_board.departures, schedule_board.arrivals):
        if train.track:
            trains.append(train)
    return trains


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    scrape()