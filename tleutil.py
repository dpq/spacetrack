from datetime import datetime, timedelta

# Root URL from which data files are retrieved
source = "http://celestrak.com/NORAD/elements/"

# Yeah, I know what TLE stands for :-) Still, entries are comprised of three lines, one being occupied by the sat.name
linecount = 3

def parseDT(buffer):
    yearPos, yearLen = 18, 2
    floatDayPos, floatDayLen = 20, 13
    secondsInDay = 24*60*60

    buff = buffer.split("\n")

    if len(buff) < linecount:
        logging.error("TLE file too short.\n" + buffer)
        return None

    if len(buff[1]) < floatDayPos + floatDayLen:
        logging.error("Corrupted datetime entry.\n" + buffer)
        return None

    try:
        year = buff[1][yearPos : yearPos + yearLen]
        dt = datetime.strptime(year, "%y")
    except ValueError:
        logging.error("Cannot extract year value from %s" % year)
        return None

    day = buff[1][floatDayPos : floatDayPos + floatDayLen]
    if len(day.split(".")) != 2:
        logging.error("Cannot extract day value from %s" % day)
        return None

    try:
        dayOfYear, partOfDay = day.split(".")
        dayOfYear = int(dayOfYear)
        partOfDay = float("0." + partOfDay)
    except ValueError:
        logging.error("Cannot parse day value: %s is not a float" % day)
        return None

    dt += timedelta(days = dayOfYear - 1) + timedelta(seconds = int(secondsInDay * partOfDay))
    return dt


def parseTLE(tleLines):
    name = tleLines[0].strip()
    noradid = int(tleLines[2].split()[1])
    body = "\n".join([tleLines[0].strip(), tleLines[1], tleLines[2]]) + "\n"
    timestamp = parseDT(body)
    return noradid, name, body, timestamp
