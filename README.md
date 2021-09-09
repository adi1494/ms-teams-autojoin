# MS Teams Autojoin

**Joins online classes on ms-teams according to the timetable**

## Environment Setup

Navigate inside this directory. Create virtual environment, activate and install the required libraries

```sh
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```

Next, we can run the main process using

```sh
python3 ms-teams-autojoin.py
```

### Credentials Setup

Inside the working directory, create a `.env` file with the following specifications

```sh
TEAMS_USERNAME="email_address"
TEAMS_PASSWORD="password"
SPREADSHEET_KEY="id_of_google_sheet"
SERVICE_ACCOUNT_CREDENTIALS="minified_json_credentials"
```

### CSV Format

The script uses a `timetable.csv` file to join classes. First row of the csv should contain timings. Here is the routine for monday

```csv
Day,9:00,10:00,11:00,12:00,13:30,14:30,15:30,16:30
Mon,IE,PPLE,DM,PM,0,0,SC,0
```

- `0` means no class for that corresponding time  
- if there is an entry, it uses a dictionary to map to the correct team name  
- have to make that manually

### Create a dictionary

Maps to some unique string in the team name

```py
class_dict = {
    'IE': 'industrial',
    'PPLE': 'mt130',
    'SC':'ec419',
    'NNFS':'fuzzy',
    'DM':'ce429',
    'PM':'pe309'
}
```

**Thats all Folks!! :)**
