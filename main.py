import hashlib
from pathlib import Path
import json
import os
import time
from datetime import datetime

def getInput():
    folderPath = Path(input("Choose directory: "))
    
    while not folderPath.is_dir():
        folderPath = Path(input("Choose valid directory: "))
    
    return folderPath

def scanFiles(directory):
    hashList = {}
    
    for item in directory.iterdir():
        if item.is_file():
            fileInfo = os.stat(item)
            ctime = time.ctime(fileInfo.st_mtime)
            dt = datetime.strptime(ctime, "%c")
            modTime = dt.strftime("%Y-%m-%d %H:%M:%S")
            
            hashList[item.name] = [calculateFileHash(item), modTime]
    return hashList

def calculateFileHash(filePath):
    with open(filePath, "rb") as file:
        content = file.read()
    
    hashValue = hashlib.sha256(content)
    return hashValue.hexdigest()

def compare(hashList):
    with open("baseline.json", "r") as file:
        unchanged = {}
        changed = {}
        removed = {}
        hashListCopy = hashList.copy()
        baselineHashList = json.load(file)
        for item in baselineHashList:
            value = baselineHashList.get(item)[0]
            change = determineChangeType(value, item, hashList)
            match change:
                case "U":
                    unchanged[item] = baselineHashList.get(item)
                case "C":
                    changed[item] = hashListCopy.get(item)
                    printToLog("CHANGED", item)
                case "R":
                    removed[item] = baselineHashList.get(item)
                    printToLog("REMOVED", item)
        
        for item in hashList:
            printToLog(" ADDED ", item)
        printCompareResults(unchanged, changed, hashList, removed)

def printToLog(event, item):
    dt = datetime.strptime(time.ctime(), "%c")
    noticeTime = dt.strftime("%Y-%m-%d %H:%M:%S")
    printLine = noticeTime + " | " + event + " | " + item
    with open("fim.log", "a") as logFile:
        print(printLine, file=logFile)

def determineChangeType(value, item, hashList):
    if item in hashList:
        checkValue = hashList.get(item)[0]
        hashList.pop(item)
        if value == checkValue:
            return "U"
        else:
            return "C"
    else:
        return "R"

def printCompareResults(unchanged, changed, hashList, removed):
    if unchanged:
        print("\nUnchanged:")
        for item in unchanged:
            print("  " + item)
    
    if changed:
        print("\nChanged:")
        for item in changed:
            print("  " + item + " Changed: " + changed.get(item)[1])
    
    if hashList:
        print("\nAdded:")
        for item in hashList:
            print("  " + item)
    
    if removed:
        print("\nRemoved:")
        for item in removed:
            print("  " + item)

def create(hashList):
    if Path("baseline.json").is_file():
        print("Baseline already exists")
    else:
        with open("baseline.json", "w", encoding="utf-8") as file:
            json.dump(hashList, file, indent=4)

def reset(hashList):
    if Path("baseline.json").is_file():
        with open("baseline.json", "w", encoding="utf-8") as file:
            json.dump(hashList, file, indent=4)
    else:
        createNew = input("Baseline does not exist. Would you like to create one? Y/N: ").lower()
        if createNew == "y":
            create(hashList)

def compareBaselineExist(hashList):
    if not Path("baseline.json").is_file(): 
        createNew = input("Baseline does not exist. Would you like to create one? Y/N: ").lower()
        if createNew == "y":
            create(hashList)
            return False
    return True

def viewLog():
    with open("fim.log", "r") as logFile:
        for event in logFile:
            print(event)


def handleChoice(hashList):
    hashListCopy = hashList.copy()
    choice = input("Create, Reset, Compare, or View Log?: ").lower()
    if choice == "create":
        create(hashList)
    elif choice == "reset":
        reset(hashList)
    elif choice == "compare":
        if not compareBaselineExist(hashList):
            return
        compare(hashList)
        if input("\nWould you like to update your baseline? Y/N: ").lower() == "y":
            reset(hashListCopy)
    elif choice == "view log":
        viewLog()

def main():
    directory = getInput()
    hashList = scanFiles(directory)
    handleChoice(hashList)

if __name__ == "__main__":
    main()