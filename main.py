import os
import argparse

import config

clean = True

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

    from logicInterface import testDungeons, testOverworld

    if args.dungeons:
        args.dungeons = [int(x[0]) for x in args.dungeons]

    # startTime = datetime.datetime.now()

    if args.testDungeons:
        testDungeons(args.dungeons or config.dungeons)
    if args.testOverworld:
        testOverworld()
    
    # duration = datetime.datetime.now() - startTime

    # print(f"Duration: {duration}")

    if clean:
        print("No logic differences found!")

main()