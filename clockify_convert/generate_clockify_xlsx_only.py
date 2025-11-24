#!/usr/bin/env python3
"""
XLSX-Only Clockify Generator (ohne odfpy)
Liest KW-Sheet und schreibt Clockify-Sheet in XLSX-Dateien
"""

import sys
import re
import os
import pandas as pd
from datetime import datetime, timedelta

def extract_week_number(filename):
    """Extract week number from filename (e.g., '25KW06' -> '06')"""
    match = re.search(r'KW(\d{2})', filename)
    if match:
        return match.group(1)
    return ''

def parse_date(date_str):
    """Parse date from various formats"""
    # Try format: "Mo 17.11.2025" or "Di 18.11.2025"
    match = re.search(r'(\d{2}\.\d{2}\.\d{4})', str(date_str))
    if match:
        return match.group(1)
    
    # Try ISO format: "2025-11-17"
    match = re.search(r'(\d{4})-(\d{2})-(\d{2})', str(date_str))
    if match:
        year, month, day = match.groups()
        return f"{day}.{month}.{year}"
    
    return None

def parse_time(time_val):
    """Parse time from Excel time value or string"""
    if pd.isna(time_val):
        return None
    
    # If it's already a string in HH:MM format
    if isinstance(time_val, str):
        match = re.search(r'(\d{1,2}):(\d{2})', time_val)
        if match:
            return f"{int(match.group(1)):02d}:{match.group(2)}"
    
    # If it's a pandas Timestamp or datetime
    if isinstance(time_val, (pd.Timestamp, datetime)):
        return time_val.strftime('%H:%M')
    
    # If it's a float (Excel time format: fraction of a day)
    try:
        time_float = float(time_val)
        hours = int(time_float * 24)
        minutes = int((time_float * 24 * 60) % 60)
        return f"{hours:02d}:{minutes:02d}"
    except:
        pass
    
    return None

def hours_to_duration(hours_val):
    """Convert hours to hh:mm:ss format"""
    if pd.isna(hours_val):
        return "00:00:00"
    
    try:
        hours = float(hours_val)
        h = int(hours)
        m = int((hours - h) * 60)
        return f"{h:02d}:{m:02d}:00"
    except:
        return "00:00:00"

def time_to_minutes(time_str):
    """Convert time string 'HH:MM' to minutes"""
    if not time_str:
        return 0
    try:
        parts = time_str.split(':')
        return int(parts[0]) * 60 + int(parts[1])
    except:
        return 0

def minutes_to_time(minutes):
    """Convert minutes to time string 'HH:MM'"""
    h = minutes // 60
    m = minutes % 60
    return f"{h:02d}:{m:02d}"

def is_activity_row(row):
    """Check if row is an activity entry"""
    col_a = str(row[0]) if len(row) > 0 else ''
    col_b = str(row[1]) if len(row) > 1 else ''
    
    # Check if col_a has tags pattern (e.g., "TH1,2" or "TH1")
    has_tags = bool(re.match(r'TH[\d,]+', col_a))
    # Check if col_b has description
    has_description = len(col_b) > 0 and col_b not in ['Start', 'Anreise', 'ausgeführte Tätigkeiten', 'nan']
    
    # Accept rows even with empty or 0 hours
    return has_tags and has_description

def extract_activities(df, project, client, email, kalenderwoche):
    """Extract activity entries from KW sheet DataFrame"""
    activities = []
    current_date = None
    current_task = None
    current_start_time = None
    cumulative_minutes = 0
    
    # Convert DataFrame to list of lists for easier processing
    rows = df.values.tolist()
    
    for i, row in enumerate(rows):
        if len(row) < 2:
            continue
        
        col_a = str(row[0]) if not pd.isna(row[0]) else ''
        col_b = str(row[1]) if len(row) > 1 and not pd.isna(row[1]) else ''
        
        # Check for date row (e.g., "Mo 17.11.2025" or "Di 18.11.2025")
        date = parse_date(col_a)
        if date:
            current_date = date
            cumulative_minutes = 0
            
            # Try to get start time from column C (index 2)
            if len(row) > 2:
                start_time = parse_time(row[2])
                if start_time:
                    current_start_time = start_time
            continue
        
        # Check for task row (e.g., "Dienstag, Einzelraumregelung")
        if ',' in col_a and not col_a.startswith('TH'):
            parts = col_a.split(',', 1)
            if len(parts) > 1:
                current_task = parts[1].strip()
                cumulative_minutes = 0
                continue
        
        # Check if this is an activity row
        if is_activity_row(row):
            tags = col_a
            description = col_b
            duration_hours = row[6] if len(row) > 6 else 0  # Column G
            duration = hours_to_duration(duration_hours)
            
            # Calculate start time for this activity
            if current_start_time:
                start_time = minutes_to_time(time_to_minutes(current_start_time) + cumulative_minutes)
            else:
                start_time = "08:00"
            
            # Update cumulative time
            try:
                hours = float(duration_hours)
                cumulative_minutes += int(hours * 60)
            except:
                pass
            
            activity = {
                'Project': project,
                'Client': client,
                'Description': description,
                'Task': current_task or '',
                'Email': email,
                'Tags': tags,
                'Billable': 'Yes',
                'Start Date': current_date or '',
                'Start Time': start_time,
                'Duration (hh:mm:ss)': duration
            }
            activities.append(activity)
    
    return activities

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 generate_clockify_xlsx_only.py <input.xlsx> <email>")
        print("Example: python3 generate_clockify_xlsx_only.py 25KW06.xlsx user@example.com")
        print("")
        print("Das Skript liest das KW-Sheet und schreibt die Clockify-Daten")
        print("in das clockify-Sheet der gleichen Datei.")
        sys.exit(1)
    
    input_file = sys.argv[1]
    email = sys.argv[2]
    
    # Check if file is XLSX
    if not input_file.lower().endswith('.xlsx'):
        print(f"❌ Nur XLSX-Dateien werden unterstützt: {input_file}")
        sys.exit(1)
    
    # Extract week number from filename
    kalenderwoche = extract_week_number(os.path.basename(input_file))
    
    print(f"📖 Lese XLSX-Datei: {input_file}")
    
    try:
        # Read KW sheet
        df_kw = pd.read_excel(input_file, sheet_name='KW', header=None)
        
        # Get project and client
        project = str(df_kw.iloc[7, 1]) if len(df_kw) > 7 else "Unknown Project"
        client = str(df_kw.iloc[0, 0]) if len(df_kw) > 0 else "Unknown Client"
        
        print(f"📋 Project: {project}")
        print(f"👤 Client: {client}")
        print(f"📧 Email: {email}")
        print(f"📅 Kalenderwoche: {kalenderwoche}")
        print()
        
        # Extract activities
        print("🔍 Extrahiere Tätigkeiten...")
        activities = extract_activities(df_kw, project, client, email, kalenderwoche)
        
        print(f"✅ {len(activities)} Einträge gefunden")
        print()
        
        # Create clockify DataFrame
        clockify_data = []
        for act in activities:
            clockify_data.append([
                act['Project'], act['Client'], act['Description'], act['Task'],
                act['Email'], act['Tags'], act['Billable'], act['Start Date'],
                act['Start Time'], act['Duration (hh:mm:ss)']
            ])
        
        df_clockify = pd.DataFrame(clockify_data, columns=[
            'Project', 'Client', 'Description', 'Task', 'Email', 'Tags',
            'Billable', 'Start Date', 'Start Time', 'Duration (hh:mm:ss)'
        ])
        
        # Write back to the same file
        print(f"📝 Schreibe Clockify-Sheet...")
        with pd.ExcelWriter(input_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df_clockify.to_excel(writer, sheet_name='clockify', index=False)
        
        print(f"✅ Erfolgreich gespeichert: {input_file}")
        print()
        print("📊 Generierte Einträge:")
        for i, act in enumerate(activities[:10], 1):
            desc = act['Description'][:50] + '...' if len(act['Description']) > 50 else act['Description']
            print(f"  {i}. {act['Start Date']} {act['Start Time']} - {desc} ({act['Duration (hh:mm:ss)']})")
        
        if len(activities) > 10:
            print(f"  ... und {len(activities) - 10} weitere")
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
