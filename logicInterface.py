import os
import sys
import json
import datetime
import itertools
import config

sys.path.append(config.referenceLadxrPath)

from locations.items import *
import explorer
import logic
from worldSetup import WorldSetup, start_locations
from settings import *
from entranceInfo import ENTRANCE_INFO

try:
    os.unlink("newLogic")
except:
    pass

os.symlink(config.newLogicPath, 'newLogic', target_is_directory=True)
sys.path.append(config.newLogicPath)

from newLogic.main import Logic as NewLogic

dungeonItems = (
    ( # D0
        (STONE_BEAK0, 1),
        (POWER_BRACELET, 1),
        (SHIELD, 1),
        (KEY0, 3),
        (SWORD, 1),
        (KEY0, 2, 1),
        (MAGIC_POWDER, 1),
        (PEGASUS_BOOTS, 1),
        (FEATHER, 1),
        (NIGHTMARE_KEY0, 1),
        (BOW, 1),
        (BOMB, 1),
    ),
    ( # D1
        (BOMB, 1),
        (SHIELD, 1),
        (KEY1, 3),
        (STONE_BEAK1, 1),
        (FEATHER, 1),
        (NIGHTMARE_KEY1, 1),
        (SWORD, 1),
        (BOOMERANG, 1),
        (MAGIC_POWDER, 1),
    ),
    ( # D2
        (POWER_BRACELET, 1),
        (KEY2, 5),
        (FEATHER, 1),
        (HOOKSHOT, 1),
        (MAGIC_POWDER, 1),
        (MAGIC_ROD, 1),
        (KEY2, 3),
        (STONE_BEAK2, 1),
        (BOW, 1),
        (OCARINA, 1),
        (SONG1, 1),
        (SWORD, 1),
        (NIGHTMARE_KEY2, 1),
    ),
    ( # D3
        (PEGASUS_BOOTS, 1),
        (POWER_BRACELET, 1),
        (KEY3, 8),
        (STONE_BEAK3, 1),
        (KEY3, 4),
        (BOMB, 1),
        (FEATHER, 1),
        (NIGHTMARE_KEY3, 1),
        (SWORD, 1),
        (MAGIC_POWDER, 1),
        (BOOMERANG, 1),
    ),
    ( # D4
        (SHIELD, 1),
        (SWORD, 1),
        (FEATHER, 1),
        (PEGASUS_BOOTS, 1),
        (BOMB, 1),
        (FLIPPERS, 1),
        (KEY4, 1),
        (KEY4, 2),
        (KEY4, 3),
        (STONE_BEAK4, 1),
        (POWER_BRACELET, 1),
        (NIGHTMARE_KEY4, 1),
        (BOOMERANG, 1),
        (HOOKSHOT, 1),
        (MAGIC_POWDER, 1),
    ),
    ( # D5
        (HOOKSHOT, 1), 
        (SWORD, 1), 
        (FEATHER, 1), 
        (KEY5, 1), 
        (KEY5, 2), 
        (STONE_BEAK5, 1), 
        (BOMB, 1), 
        (PEGASUS_BOOTS, 1), 
        (POWER_BRACELET, 1), 
        (FLIPPERS, 1), 
        (NIGHTMARE_KEY5, 1), 
        (BOOMERANG, 1), 
        (MAGIC_POWDER, 1),
        (MAGIC_ROD, 1),
    ),
    ( # D6
        (POWER_BRACELET, 1),
        (POWER_BRACELET, 2),
        (STONE_BEAK6, 1),
        (BOMB, 1),
        (FEATHER, 1),
        (BOOMERANG, 1),
        (BOW, 1),
        (KEY6, 1),
        (KEY6, 2),
        (OCARINA, 1),
        (SONG1, 1),
        (PEGASUS_BOOTS, 1),
        (HOOKSHOT, 1),
        (NIGHTMARE_KEY6, 1),
        (MAGIC_POWDER, 1),
    ),
    ( # D7
        (KEY7, 1),
        (KEY7, 3),
        (STONE_BEAK7, 1),
        (POWER_BRACELET, 1),
        (BOMB, 1),
        (FEATHER, 1),
        (SHIELD, 1),
        (HOOKSHOT, 1),
        (NIGHTMARE_KEY7, 1),
        (SHIELD, 2),
        (SWORD, 1),
        (PEGASUS_BOOTS, 1),
        (MAGIC_POWDER, 1),
    ),
    ( # D8
        (FEATHER, 1),
        (HOOKSHOT, 1),
        (MAGIC_ROD, 1),
        (STONE_BEAK8, 1),
        (POWER_BRACELET, 1),
        (KEY8, 1),
        (KEY8, 2),
        (KEY8, 4),
        (BOMB, 1),
        (SWORD, 1),
        (BOW, 1),
        (NIGHTMARE_KEY8, 1),
        (PEGASUS_BOOTS, 1),
        (MAGIC_POWDER, 1),
        (FLIPPERS, 1),
    )
)

overworldItems = (
    (FEATHER, 1),
    (HOOKSHOT, 1),
    (SWORD, 1),
    (ROOSTER, 1),
    (POWER_BRACELET, 1),
    (BOMB, 1),
    (BOW, 1),
    (PEGASUS_BOOTS, 1),
    (MAGIC_POWDER, 1),
    (FLIPPERS, 1),
    (MAGIC_ROD, 1),
    (BOOMERANG, 1),
    (SHIELD, 1),
    (RUPEES_500, 4),
)

randomStartItems = (
    (FEATHER, 1),
    (HOOKSHOT, 1),
    (SWORD, 1),
    (ROOSTER, 1),
    (POWER_BRACELET, 1),
    (BOMB, 1),
    (PEGASUS_BOOTS, 1),
    (MAGIC_POWDER, 1),
    (FLIPPERS, 1),
    (BOOMERANG, 1),
    (SHIELD, 1),
)

ignoredNames = {"0x14C", "0x150", "MS2_KILL", "MS1_KILL", "MS3_KILL"}
difficulties = ('casual', '', 'hard', 'glitched', 'hell')

def visitLogic(log, inventory):
    e = explorer.Explorer()

    for item in inventory:
        for j in range(item[1]):
            e.addItem(item[0])

    e.visit(log.start)
    locations = e.getAccessableLocations()

    names = set()

    for location in locations:
        for item in location.items:
            names.add(item.nameId)

    return names

def compareLogics(log, newLog, inventory):
    global clean

    names = visitLogic(log, inventory)
    newNames = visitLogic(newLog, inventory)

    if names != newNames:
        diff = {}
        diff['items'] = {}
        for pair in inventory:
            diff['items'][pair[0]] = pair[1]
        diff['common'] = list(names.intersection(newNames))
        diff['old'] = list(names.difference(newNames))
        diff['new'] = list(newNames.difference(names))
        diff['logic'] = log.settings.logic
        diff['owls'] = log.settings.owlstatues
        if newNames.difference(names).difference(ignoredNames) or names.difference(newNames).difference(ignoredNames):
            diffStr = json.dumps(diff)
            print(f"Difference found:\n{diffStr}")
            clean = False
            with open('diffs.log', 'a') as oFile:
                oFile.write(f'{diffStr}\n')

def testDungeon(dungeonNum, settings):
    worldSetup = WorldSetup()
    worldSetup.goal = "8"
    worldSetup.entrance_mapping['start_house:inside'] = f'd{dungeonNum}:inside'
    worldSetup.entrance_mapping[f'd{dungeonNum}:inside'] = f'start_house:inside'
    log = logic.main.Logic(settings, world_setup=worldSetup)
    newLog = NewLogic(settings, world_setup=worldSetup)
    items = dungeonItems[dungeonNum]
    log.settings = settings

    addForcedItems(log)
    addForcedItems(newLog)

    testItems(items, log, newLog)

def addForcedItems(logic):
    for loc in logic.location_list:
        for ii in [x for x in loc.items if len(x.OPTIONS) == 1]:
            ii.item = ii.OPTIONS[0]

def testOverworldSettings(settings, entranceMap, items, fixedItems=False):
    worldSetup = WorldSetup()
    worldSetup.goal = "8"

    for i in range(9):
        dungeon = f'd{i}'
        if dungeon not in entranceMap:
            worldSetup.entrance_mapping[dungeon] = 'start_house:inside'
    
    for entrance in entranceMap:
        worldSetup.entrance_mapping[entrance] = entranceMap[entrance]

    log = logic.main.Logic(settings, world_setup=worldSetup)
    newLog = NewLogic(settings, world_setup=worldSetup)

    log.settings = settings

    addForcedItems(log)
    addForcedItems(newLog)

    if fixedItems:
        compareLogics(log, newLog, items)
    else:
        testItems(items, log, newLog)

def testItems(items, log, newLog):
    totalCombos = 0
    start = datetime.datetime.now()

    for i in range(len(items) + 1):
        combos = itertools.combinations(items, i)

        for combo in combos:
            compareLogics(log, newLog, combo)
            totalCombos += 1
    
    duration = datetime.datetime.now() - start

    # print(f"Tested {totalCombos} combinations, {duration / totalCombos} each")

def testDiscordScenario():
    # Brute force entrance possibilities to check for a logic bug
    settings = Settings()
    pool = [f'{x}:inside' for x in ENTRANCE_INFO if ENTRANCE_INFO[x].type in ['single', 'water', 'trade', 'dungeon']]
    mapped = ('d2', 'shop', 'trendy_shop', 'kennel')
    items = (
        (SWORD, 2),
        (MAGIC_POWDER, 1),
        (SHOVEL, 1),
        (MAX_BOMBS_UPGRADE, 1),
        (BLUE_TUNIC, 1),
        (RED_TUNIC, 1),
        (FLIPPERS, 1),
        (HOOKSHOT, 1),
        (BOWWOW, 1),
        (SONG3, 1),
        (GOLD_LEAF, 2),
        (SEASHELL, 9),
        (TRADING_ITEM_BANANAS, 1),
        (TRADING_ITEM_STICK, 1),
        (TRADING_ITEM_HONEYCOMB, 1),
        (TRADING_ITEM_HIBISCUS, 1),
        (TRADING_ITEM_BROOM, 1),
        (TRADING_ITEM_NECKLACE, 1),
        (KEY0, 3),
        (KEY2, 1),
        (KEY3, 4),
        (KEY4, 3),
        (KEY5, 1),
        (KEY6, 1),
        (KEY7, 1),
        (KEY8, 2),
    )

    combo = 1
    for chosen in itertools.combinations(pool, 4):
        # for targets in itertools.permutations(mapped):
        entranceMap = {}

        for i in range(len(mapped)):
            entranceMap[mapped[i]] = chosen[i]
        
        worldSetup = WorldSetup()
        worldSetup.goal = "8"
        
        for outside, inside in entranceMap.items():
            worldSetup.entrance_mapping[outside] = inside
            worldSetup.entrance_mapping[inside] = outside

        log = logic.Logic(settings, world_setup=worldSetup)
        names = visitLogic(log, items)

        if '0x0A6' in names and '0x28A' not in names:
            pass
        
        # print(f"Combo #{combo}")
        
        combo += 1

def testDungeons(dungeons=range(9)):
    settings = Settings()

    for i in dungeons:
        for difficulty in difficulties:
            # print(f"Testing dungeon {i} {difficulty} logic")
            settings.logic = difficulty
            testDungeon(i, settings)

    settings.owlstatues = "both"
    for i in dungeons:
        for difficulty in difficulties:
            # print(f"Testing dungeon {i} {difficulty} logic with owls")
            settings.logic = difficulty
            testDungeon(i, settings)

def testOverworld():
    settings = Settings()

    for difficulty in difficulties:
        # print(f'Testing vanilla overworld "{difficulty}" logic')
        settings.logic = difficulty

        testOverworldSettings(settings, {}, overworldItems)

        worldSetup = WorldSetup()
        emptyEntrances = {}
        for entrance in [x for x in worldSetup.entrance_mapping if ':inside' not in x]:
            emptyEntrances[entrance] = 'start_house:inside'
        
        for start in [x for x in worldSetup.entrance_mapping if ':inside' not in x]:
            entranceMap = emptyEntrances.copy()
            entranceMap['start_house:inside'] = start

            # print(f'Testing start location {start} "{difficulty}" logic')

            testOverworldSettings(settings, entranceMap, randomStartItems)