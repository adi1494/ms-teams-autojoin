# MS Teams Autojoin

**Joins online classes on ms-teams according to the timetable**  

## using your routine
The script uses a timetable.csv file to join classes  

### CSV Format
First row of the csv should contain timings
> Day,9:00,10:00,11:00,12:00,13:30,14:30,15:30,16:30

Here is the routine for monday
> Mon,IE,PPLE,DM,PM,0,0,SC,0

> 0 means no class for that corresponding time  
> if there is an entry, it uses a dictionary to map to the correct team name  
> have to make that manually

### Create a dictionary
Maps to some unique string in the team name  
>   `class_dict = {
            'IE': 'industrial',
            'PPLE': 'mt130',
            'SC':'ec419',
            'NNFS':'fuzzy',
            'DM':'ce429',
            'PM':'pe309'
        }
    `

## logging in with your user id
enter your credentials in the script
> if your email is example@email.com and password is examplepassword  
> change the line in the script as  
> `CREDS = {'email' : 'example@email.com','passwd':'examplepassword'}`

**Thats all Folks!! :)**

