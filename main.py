import os
import sys
import json
import argparse
import datetime
from multiprocessing import Manager

import config

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
    parser.add_argument('--performance-only', dest='perfTest', action='store_true', help='Only run the performance test. Tests the reference version, not the new one.')
    parser.add_argument('--time-per-dungeon', dest='timePerDungeon', type=int, default=60, help='Target time per dungeon in seconds for the performance test. Default is 60 seconds.')
    args = parser.parse_args()

    config.referenceLadxrPath = args.referenceLadxrPath or config.referenceLadxrPath 
    config.newLogicPath = args.newLogicPath or config.newLogicPath 

    try:
        os.unlink("newLogic")
    except:
        pass

    os.symlink(config.newLogicPath, 'newLogic', target_is_directory=True)
    sys.path.append(config.newLogicPath)
    sys.path.append(config.referenceLadxrPath)

    import logicInterface

    if args.dungeons:
        args.dungeons = [int(x[0]) for x in args.dungeons]
    
    dungeons = args.dungeons or config.dungeons
    
    startTime = datetime.datetime.now()

    if args.perfTest:
        print(f"Starting performance tests")

        for dungeon in dungeons:
            logicInterface.perfTest(dungeon, 'hell', args.timePerDungeon)
        
        print(f"All performance tests done in {datetime.datetime.now() - startTime}")

        return

    processes = []
    diffs = {}

    with Manager() as manager:
        sharedDiffs = manager.dict()

        if args.testDungeons:
            processes.extend(logicInterface.testDungeons(sharedDiffs, dungeons))
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

if __name__ == '__main__':
    main()