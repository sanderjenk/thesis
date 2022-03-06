def mapOldDefaultPriorities(argument):
    switcher = {
        "Trivial": 1,
        "Minor": 2,
        "Major": 3,
        "Critical": 4,
        "Blocker": 5,
    }
    return switcher.get(argument, 1)

def mapDefaultPriorities(argument):
    switcher = {
        "Lowest": 1,
        "Low": 2,
        "Medium": 3,
        "High": 4,
        "Highest": 5,
    }
    return switcher.get(argument, 1)

def mapHybridPriorities(argument):
    switcher = {
        "Trivial": 1,
        "Low": 2,
        "Medium": 3,
        "High": 4,
        "Critical": 5,
    }
    return switcher.get(argument, 1)

def mapCompassPriorities(argument):
    switcher = {
        "Trivial - P5": 1,
        "Minor - P4": 2,
        "Major - P3": 3,
        "Critical - P2": 4,
        "Blocker - P1": 5,
    }
    return switcher.get(argument, 1)

def mapDnnPriorities(argument):
    switcher = {
        "Low": 1,
        "Medium": 2,
        "High": 3,
        "Blocker": 4,
    }
    return switcher.get(argument, 1)

def getPriorityMapper(project):
    switcher = {
        "COMPASS":mapCompassPriorities,
        "DATACASS": mapOldDefaultPriorities,
        "FAB": mapDefaultPriorities,
        "IS": mapDefaultPriorities,
        "MDL":mapOldDefaultPriorities,
        "MOBILE":mapOldDefaultPriorities,
        "STL":mapDefaultPriorities,
        "apstud":mapHybridPriorities,
        "dnn":mapDnnPriorities,
        "mesos": mapOldDefaultPriorities,
        "mule":mapOldDefaultPriorities,
        "nexus":mapOldDefaultPriorities,
        "timob":mapHybridPriorities,
        "tistud":mapHybridPriorities,
        "xd": mapOldDefaultPriorities,
    }
    return switcher.get(project, mapDefaultPriorities)

def mapPriority(project, priority):
    mapper = getPriorityMapper(project)
    return mapper(priority)
