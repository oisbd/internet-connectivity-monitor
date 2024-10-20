# Internet Connection Monitor

## How the Script Works

### Monitoring Internet Connection
- The script checks the internet connection every 3 minutes.
- It attempts to reach http://www.google.com with a timeout of 10 seconds.
- The result determines if the internet is CONNECTED or NOT CONNECTED.

### Recording Internet Speed
- When the internet is CONNECTED, it measures the download and upload speeds using the speedtest-cli module.
- Speeds are recorded in bits per second (bps).

### Logging Events
Events are logged in a CSV file with columns:
- Timestamp: Date and time of the event.
- Event: Description of the event (e.g., "CONNECTED", "NOT CONNECTED").
- Download_Speed_bps: Measured download speed.
- Upload_Speed_bps: Measured upload speed.

The script keeps track of the previous status to identify when the internet goes down or comes back up.

### Generating Reports
The `generate_report` function reads the CSV log file and compiles:
- Downtime Intervals: Periods when the internet was not connected.
- Internet Speeds: Recorded download and upload speeds.

The report is saved as a text file in the same directory.

## Running the Script in the Background
On Linux/macOS, you can run the script in the background using:

```bash
nohup python internet_monitor.py &
```

## Cloning the Project on Another Machine

If you or someone else needs to run the project on another machine:

1. **Clone or Copy the Project Files:**
   - Ensure that the `internet_monitor.py` and `requirements.txt` files are included.

2. **Create and Activate a New Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. **Install Packages from requirements.txt:**
   ```bash
   pip install -r requirements.txt
   ```
   This installs all the packages listed in `requirements.txt` into the virtual environment.

4. **Run the Script:**
   ```bash
   python internet_monitor.py
   ```
