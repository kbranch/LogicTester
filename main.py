import os
import json
import argparse
import datetime
from multiprocessing import Manager

import config
import logicInterface

def dirPath(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dungeons', dest='dungeons', type=list, nargs='+', help='List of dungeons to check, e.g. "--dungeons 0 1 5 6"')
    parser.add_argument('--no-dungeons', dest='testDungeons', action='store_false', help='Don\'t test any dungeons')
    parser.add_argument('--no-overworld', dest='testOverworld', action='store_false', help='Don\'t test the overworld')
    parser.add_argument('--reference-ladxr-path', dest='referenceLadxrPath', action='store', type=dirPath, help='Path to the main LADXR folder for the reference logic')
    parser.add_argument('--new-logic-path', dest='newLogicPath', action='store', type=dirPath, help='Path to the "logic" folder that should be compared against the reference')
    args = parser.parse_args()

    config.referenceLadxrPath = args.referenceLadxrPath or config.referenceLadxrPath 
    config.newLogicPath = args.newLogicPath or config.newLogicPath 

    if args.dungeons:
        args.dungeons = [int(x[0]) for x in args.dungeons]

    startTime = datetime.datetime.now()

    processes = []
    diffs = {}

    with Manager() as manager:
        sharedDiffs = manager.dict()

        if args.testDungeons:
            processes.extend(logicInterface.testDungeons(sharedDiffs, args.dungeons or config.dungeons))
        if args.testOverworld:
            processes.extend(logicInterface.testOverworld(sharedDiffs))
    
        for process in processes:
            process.join()
        
        for value in sharedDiffs.values():
            for k,v in value.items():
                if k not in diffs:
                    diffs[k] = []
                diffs[k].extend(v)
    
    duration = datetime.datetime.now() - startTime

    print(f"Duration: {duration}")
    with open('diffs.log', 'w') as oFile:
        oFile.write(f'{json.dumps(diffs, indent=3)}\n')

    if not diffs:
        print("No logic differences found!")
    else:
        print("Differences found, see diffs.log for details")

main()