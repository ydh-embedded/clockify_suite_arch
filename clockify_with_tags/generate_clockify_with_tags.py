#!/usr/bin/env python3
"""
Clockify Generator mit Tag-Support
Unterstützt: #DATE, #STARTTIME, #TASK, #LOCAL, #H
"""

import sys
import re
import os
import pandas as pd
from datetime import datetime, timedelta

def extract_week_number(filename):
    """Extract week number from filename"""
    match = re.search(r'KW(\d{2})', filename)
    if match:
        return match.group(1)
    return ''

def parse_date(date_str):
    """Parse date from format 'Mo 24.11.2025'"""
    match = re.search(r'(\d{2}\.\d{2}\.\d{4})', str(date_str))
    if match:
        return match.group(1)
    
    match = re.search(r'(\d{4})-(\d{2})-(\d{2})', str(date_str))
    if match:
        year, month, day = match.groups()
        return f"{day}.{month}.{year}"
    
    return None

def parse_time(time_val):
    """Parse time from various formats"""
    if pd.isna(time_val):
        return None
    
    if isinstance(time_val, str):
        match = re.search(r'(\d{1,2}):(\d{2})', time_val)
        if match:
            return f"{int(match.group(1)):02d}:{match.group(2)}"
    
    if isinstance(time_val, (pd.Timestamp, datetime)):
        return time_val.strftime('%H:%M')
    
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

def extract_tags_from_description(description):
    """Extract TH tags from description (e.g., 'TH1,2: ...' -> 'TH1,2')"""
    match = re.match(r'(TH[\d,\s]+):', str(description))
    if match:
        return match.group(1).strip()
    return ''

def extract_activities_with_tags(df, project, client, email, kalenderwoche):
    """Extract activities using tag-based structure"""
    activities = []
    current_date = None
    current_task = None
    current_start_time = None
    cumulative_minutes = 0
    
    rows = df.values.tolist()
    
    for i, row in enumerate(rows):
        if len(row) < 2:
            continue
        
        col_a = str(row[0]) if not pd.isna(row[0]) else ''
        col_b = str(row[1]) if len(row) > 1 and not pd.isna(row[1]) else ''
        
        # #DATE Tag - Datum und Startzeit
        if col_a == '#DATE':
            date = parse_date(col_b)
            if date:
                current_date = date
                cumulative_minutes = 0
                current_start_time = None
                
                # Suche nach #STARTTIME in Spalte C oder D
                for j in range(2, min(len(row), 6)):
                    col_val = str(row[j]) if not pd.isna(row[j]) else ''
                    if col_val == '#STARTTIME' and j+1 < len(row):
                        start_time = parse_time(row[j+1])
                        if start_time:
                            current_start_time = start_time
                            break
            continue
        
        # #TASK Tag - Task-Kategorie
        if col_a == '#TASK':
            current_task = col_b.strip()
            cumulative_minutes = 0
            continue
        
        # #LOCAL Tag - Aktivität mit Ort
        if col_a == '#LOCAL':
            description = col_b.strip()
            
            # Suche nach #H in Spalte H (Index 7)
            duration_hours = None
            if len(row) > 7:
                col_h = str(row[7]) if not pd.isna(row[7]) else ''
                if col_h == '#H' and len(row) > 8:
                    # Duration steht in Spalte I (Index 8)
                    try:
                        duration_hours = float(row[8])
                    except:
                        pass
                elif col_h != '#H':
                    # Vielleicht steht die Zahl direkt in H ohne #H Tag
                    try:
                        duration_hours = float(col_h)
                    except:
                        pass
            
            # Fallback: Suche in anderen Spalten
            if duration_hours is None:
                for j in range(6, min(len(row), 12)):
                    try:
                        val = float(row[j])
                        if val > 0:
                            duration_hours = val
                            break
                    except:
                        continue
            
            if duration_hours is None:
                duration_hours = 0
            
            duration = hours_to_duration(duration_hours)
            
            # Berechne Start Time (kumulativ)
            if current_start_time:
                start_time = minutes_to_time(time_to_minutes(current_start_time) + cumulative_minutes)
            else:
                start_time = "08:00"
            
            # Update kumulative Zeit
            cumulative_minutes += int(duration_hours * 60)
            
            # Extrahiere Tags aus Description
            tags = extract_tags_from_description(description)
            
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
        print("Usage: python3 generate_clockify_with_tags.py <input.xlsx> <email>")
        print("Example: python3 generate_clockify_with_tags.py 25-KW48.xlsx user@example.com")
        print("")
        print("Unterstützte Tags:")
        print("  #DATE      - Datum-Zeile (Spalte B: Datum)")
        print("  #STARTTIME - Start-Zeit (Spalte D: Zeit)")
        print("  #TASK      - Task-Kategorie (Spalte B: Name)")
        print("  #LOCAL     - Aktivität mit Ort (Spalte B: Beschreibung)")
        print("  #H         - Duration-Marker (Spalte H, Wert in I)")
        sys.exit(1)
    
    input_file = sys.argv[1]
    email = sys.argv[2]
    
    if not input_file.lower().endswith('.xlsx'):
        print(f"❌ Nur XLSX-Dateien werden unterstützt: {input_file}")
        sys.exit(1)
    
    kalenderwoche = extract_week_number(os.path.basename(input_file))
    
    print(f"📖 Lese XLSX-Datei: {input_file}")
    
    try:
        df_kw = pd.read_excel(input_file, sheet_name='KW', header=None)
        
        # Get project and client
        project = str(df_kw.iloc[6, 1]) if len(df_kw) > 6 and not pd.isna(df_kw.iloc[6, 1]) else "Unknown Project"
        client = str(df_kw.iloc[0, 0]) if len(df_kw) > 0 and not pd.isna(df_kw.iloc[0, 0]) else "Unknown Client"
        
        print(f"📋 Project: {project}")
        print(f"👤 Client: {client}")
        print(f"📧 Email: {email}")
        print(f"📅 Kalenderwoche: {kalenderwoche}")
        print()
        
        print("🔍 Extrahiere Tätigkeiten mit Tags...")
        activities = extract_activities_with_tags(df_kw, project, client, email, kalenderwoche)
        
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
        
        # Write to clockify sheet
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
