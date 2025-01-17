import sqlite3
import random
import json


def find_tier(CR):
    conn = sqlite3.connect('loot.db')
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM cr_tier where min_cr <= {CR} and max_cr >= {CR};")
    results = cursor.fetchone()


    conn.close()
    return results[1]

def get_loot(loot_type, roll, tier):


    conn = sqlite3.connect('loot.db')
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM {loot_type} where min_roll <= {roll} and max_roll >= {roll} and tier = '{tier}';")
    results = cursor.fetchall()
    conn.close()


    return results


def roll_nd(amount):
    num_dice, dice_type = amount.split('d')
    num_dice = int(num_dice)
    dice_type = int(dice_type)
    rolls = []
    for _ in range(num_dice):
        rolls.append(random.randint(1, dice_type))
    return sum(rolls)



def roll_coins(coins):
    loot = []
    for coin, value in coins.items():
        # print(coin, value)
        
        if '*' in value:
            dice, multiplier = value.split('*')
        else:
            dice = value
            multiplier = 1

        roll = roll_nd(dice)
        multiplier = int(multiplier)
        coinage = roll * multiplier
        loot.append((coin, coinage))
    return loot


def get_art_objects(results):
    if results[0] is None and results[1] is None:
        return None  
    else:
    # print(results)
        art_type = results[0]
        art_roll = results[1]

        art_amnt = roll_nd(art_roll)
        # print(art_amnt, art_type)

        return art_amnt, art_type
    
def get_art_items(art_type):
    conn = sqlite3.connect('loot.db')
    cursor = conn.cursor()
    query = '''
        SELECT * FROM art WHERE art_type = ?;
    '''
    art_value = f'{int(art_type):,} gp Art Objects'
    cursor.execute(query, (art_value,))
    results = cursor.fetchall()
    conn.close()
    return results

def sample_art(art, art_amnt):
    selected_art = []
    
    for _ in range(art_amnt):
        roll = random.randint(0, len(art) - 1)
        
        selected_item = art[roll]
        selected_art.append(selected_item)
        
        art.remove(selected_item)
    return selected_art






def get_gem_objects(results):
    if results[0] is None and results[1] is None:
        return None 
    else:
    # print(results)
        gem_type = results[0]
        gem_roll = results[1]

        gem_amnt = roll_nd(gem_roll)
        # print(gem_amnt, gem_type)
        return gem_amnt, gem_type
    
def get_gem_items(gem_type):
    conn = sqlite3.connect('loot.db')
    cursor = conn.cursor()
    query = '''
        SELECT * FROM gems WHERE gem_type = ?;
    '''
    gem_value = f'{int(gem_type):,} gp Gemstones'
    cursor.execute(query, (gem_value,))
    results = cursor.fetchall()
    conn.close()
    return results

def sample_gems(gems, gem_amnt):
    selected_gems = []
    count = {}
    for _ in range(gem_amnt):
        roll = random.randint(0, len(gems) - 1)
        
        selected_item = gems[roll]
        if selected_item in count:
            count[selected_item] += 1
        else:
            count[selected_item] = 1
        
        
    result = [f'x{count[item]} {item}' for item in count]

    return result

def determine_magic_rolls(results):

    magic_table = results[0][9]
    magic_rolls = results[0][10]

    if not magic_rolls:

        times = 0


    elif magic_rolls == '1':
        times = 1

        # print(times)

    elif magic_rolls != '1':
        num_dice, dice_type = magic_rolls.split('d')
        num_dice = int(num_dice)
        dice_type = int(dice_type)
        times = random.randint(1, dice_type)

    return magic_table, times

def build_magic_query(magic_table, times):

    base_query = f'''
    SELECT * FROM magic_items
    WHERE table_type = 'Magic Item Table {magic_table}'
    AND (
    '''

    conditions = []

    for _ in range(times):
        roll = random.randint(1, 100)
        conditions.append(f'(min_roll <={roll} AND max_roll >= {roll})')

    query = base_query + ' OR '.join(conditions) + ');'
    return query


def roll_magic_items(query):
    conn = sqlite3.connect('loot.db')
    cursor = conn.cursor()

    cursor.execute(query)

    results = cursor.fetchall()
    conn.close()
    return results

def extract_magic_items(magic_items):
    items = []
    for item in magic_items:
        items.append(item[4])
    return items


def roll_hoard(CR):

    loot_type = 'hoard'

    tier = find_tier(CR)

    roll = random.randint(1, 100)

    loot_results = get_loot(loot_type, roll, tier)

    coins = roll_coins(json.loads(loot_results[0][2]))
    for item in coins:
        print(f'{int(item[1]):,} {item[0]}')
    art_amnt, art_type = None, None
    gem_amnt, gem_type = None, None
    
    selected_art = None
    if loot_results[0][5] and loot_results[0][6]:
        art_amnt, art_type = get_art_objects(
            (loot_results[0][5], loot_results[0][6])
        )
        art_results = get_art_items(art_type)
        art = []
        for item in art_results:
            art.append(item[2])  
        selected_art = sample_art(art, art_amnt)
        if selected_art:
            for item in selected_art:
                print(f'{item}, {int(art_type):,} gp')
            
    selected_gems = None
    if loot_results[0][7] and loot_results[0][8]:
        gem_amnt, gem_type = get_art_objects(
            (loot_results[0][7], loot_results[0][8])
        )
        gem_results = get_gem_items(gem_type)
        gems= []
        for item in gem_results:
            gems.append(item[2])
        selected_gems = sample_gems(gems, gem_amnt)
        if selected_gems:
            for item in selected_gems:
                print(f'{item}, {int(gem_type):,} gp')
        
    magic_items = None
    if loot_results[0][9] and loot_results[0][10]:
        magic_table, times = determine_magic_rolls(loot_results)

        query = build_magic_query(magic_table, times)
        rolled_items = roll_magic_items(query)
        magic_items = extract_magic_items(rolled_items)
        for item in magic_items:
            print(item)
    return (coins, selected_art, selected_gems, magic_items)
            
            
def roll_individual(CR):
    loot_type = 'individual'
    tier = find_tier(CR)
    roll = random.randint(1, 100)
    loot_results = get_loot(loot_type, roll, tier)
    coins = {}
    for item in loot_results:
        coins[item[4]] = item[5]
    coins = roll_coins(coins)
    for item in coins:
        print(f'{int(item[1]):,} {item[0]}')
    return coins
            
            
