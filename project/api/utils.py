import time
import datetime
from project import app


def calcTimeDiff(timeDays,lastDate,docID,format='%Y-%m-%dT%H:%M:%SZ'):
    '''
    Calculate the time difference between two formatted date strings
    '''
    now = datetime.datetime.now()
    lastUpdatedDate = datetime.datetime.strptime(lastDate, format)
    calcDate = abs((now - lastUpdatedDate).days) 

    if calcDate < timeDays:
        app.logger.debug(f"Calculated {calcDate} days vs setting"+ 
                         f" of {timeDays} days from {lastDate}")
        return True
    else:
        app.logger.debug(f"Calculated {calcDate} days vs setting"+ 
                         f" of {timeDays} days from {lastDate}")
        return False


def getNow(format='%Y-%m-%dT%H:%M:%SZ'):
    '''
    Calculate the current time and send it back in the format given
    '''
    return time.strftime(format)
    
def main():
    pass


if __name__ == "__main__":
    main()
    