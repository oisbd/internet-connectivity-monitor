import time
from datetime import datetime, timedelta
import urllib.request
import speedtest
import csv
import os
import pytz

# Configuration settings
CHECK_INTERVAL = 10  # Time between checks in seconds
INTERNET_CHECK_TIMEOUT = 10  # Timeout for internet connectivity check in seconds
SPEED_CHECK_URL = 'http://www.google.com'  # URL to check for internet connectivity
MIN_DOWNLOAD_SPEED = 10  # Minimum acceptable download speed in Mbps
MIN_UPLOAD_SPEED = 5  # Minimum acceptable upload speed in Mbps

def check_internet():
    try:
        urllib.request.urlopen('http://www.google.com', timeout=10)
        return True
    except:
        return False

def get_speed():
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        download_speed = st.download()
        upload_speed = st.upload()
        return download_speed, upload_speed
    except:
        return None, None

def get_filename():
    return datetime.now().strftime('internet_log_%Y-%m-%d.csv')

def main():
    dhaka_tz = pytz.timezone('Asia/Dhaka')
    prev_status = None
    down_start_time = None
    while True:
        current_status = check_internet()
        timestamp = datetime.now(dhaka_tz)
        filename = get_filename()
        file_exists = os.path.isfile(filename)
        with open(filename, 'a', newline='') as csvfile:
            fieldnames = ['Timestamp', 'Event', 'Download_Speed_bps', 'Upload_Speed_bps']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            if current_status:
                if prev_status == False:
                    # Connection came back up
                    down_end_time = timestamp
                    down_duration = down_end_time - down_start_time
                    event = f"CONNECTED (Was down for {down_duration})"
                else:
                    event = "CONNECTED"
                # Get internet speed
                download_speed, upload_speed = get_speed()
                writer.writerow({
                    'Timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'Event': event,
                    'Download_Speed_bps': download_speed,
                    'Upload_Speed_bps': upload_speed
                })
                prev_status = True
            else:
                if prev_status == True or prev_status is None:
                    # Connection just went down
                    down_start_time = timestamp
                    event = "NOT CONNECTED (Just went down)"
                else:
                    event = "NOT CONNECTED"
                writer.writerow({
                    'Timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'Event': event,
                    'Download_Speed_bps': '',
                    'Upload_Speed_bps': ''
                })
                prev_status = False
        time.sleep(CHECK_INTERVAL)

def generate_report(filename):
    dhaka_tz = pytz.timezone('Asia/Dhaka')
    
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        down_intervals = []
        speeds = []
        low_speeds = []
        down_start_time = None
        for row in reader:
            timestamp = datetime.strptime(row['Timestamp'], '%Y-%m-%d %H:%M:%S')
            event = row['Event']
            if 'NOT CONNECTED' in event:
                if down_start_time is None:
                    down_start_time = timestamp
            elif 'CONNECTED' in event:
                if down_start_time is not None:
                    down_end_time = timestamp
                    down_duration = down_end_time - down_start_time
                    down_intervals.append({
                        'start': down_start_time,
                        'end': down_end_time,
                        'duration': down_duration
                    })
                    down_start_time = None
                # Record the speed if available
                if row['Download_Speed_bps'] and row['Upload_Speed_bps']:
                    download_speed = float(row['Download_Speed_bps'])
                    upload_speed = float(row['Upload_Speed_bps'])
                    speed_data = {
                        'timestamp': timestamp,
                        'download_speed_bps': download_speed,
                        'upload_speed_bps': upload_speed
                    }
                    speeds.append(speed_data)
                    # Check if speed is below threshold
                    if (download_speed / 1e6 < MIN_DOWNLOAD_SPEED or 
                        upload_speed / 1e6 < MIN_UPLOAD_SPEED):
                        low_speeds.append(speed_data)

        # Check if there's an ongoing downtime at the end of the file
        if down_start_time is not None:
            down_end_time = timestamp  # Use the last timestamp in the file
            down_duration = down_end_time - down_start_time
            down_intervals.append({
                'start': down_start_time,
                'end': down_end_time,
                'duration': down_duration
            })

        # Now, create the report
        report = ''
        report += f"Internet Connectivity Report for {filename}\n"
        report += "\nDowntime Intervals:\n"
        if down_intervals:
            for interval in down_intervals:
                start = interval['start'].astimezone(dhaka_tz).strftime('%Y-%m-%d %I:%M:%S %p')
                end = interval['end'].astimezone(dhaka_tz).strftime('%Y-%m-%d %I:%M:%S %p')
                duration = str(interval['duration'])
                report += f"- From {start} to {end}, Duration: {duration}\n"
        else:
            report += "No downtime recorded.\n"

        report += "\nLow Speed Intervals:\n"
        if low_speeds:
            for speed in low_speeds:
                ts = speed['timestamp'].astimezone(dhaka_tz).strftime('%Y-%m-%d %I:%M:%S %p')
                dl_speed_mbps = speed['download_speed_bps'] / 1e6
                ul_speed_mbps = speed['upload_speed_bps'] / 1e6
                report += f"- {ts}: Download {dl_speed_mbps:.2f} Mbps, Upload {ul_speed_mbps:.2f} Mbps\n"
        else:
            report += "No low speed intervals recorded.\n"

        # report += "\nInternet Speeds:\n"
        # if speeds:
        #     for speed in speeds:
        #         ts = speed['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        #         dl_speed_mbps = speed['download_speed_bps'] / 1e6
        #         ul_speed_mbps = speed['upload_speed_bps'] / 1e6
        #         report += f"- {ts}: Download {dl_speed_mbps:.2f} Mbps, Upload {ul_speed_mbps:.2f} Mbps\n"
        # else:
        #     report += "No speed data recorded.\n"

        # Save the report to a text file
        report_timestamp = datetime.now(dhaka_tz).strftime('%Y-%m-%d_%I-%M-%S_%p')
        report_filename = f"{filename.rsplit('.', 1)[0]}_{report_timestamp}_report.txt"
        with open(report_filename, 'w') as report_file:
            report_file.write(report)
        print(f"Report generated: {report_filename}")

if __name__ == "__main__":
    main()
