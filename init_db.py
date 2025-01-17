import sqlite3
import json

def load_data(string):
    """Load the loot data from the JSON file."""
    with open(string, 'r') as file:
        return json.load(file)

def get_tier_from_name(name):
    """Map the challenge name to its corresponding tier."""
    tiers = {
        'Challenge 0-4': 'Tier_1',
        'Challenge 5-10': 'Tier_2',
        'Challenge 11-16': 'Tier_3',
        'Challenge 17+': 'Tier_4'
    }
    return tiers.get(name, None)

def process_individual_data(data):
    """Process the individual data into a format for database insertion."""
    individual = []
    for table in data['individual']:
        tier = get_tier_from_name(table['name'])
        if tier:
            for entry in table['table']:
                min_roll = entry['min']
                max_roll = entry['max']
                coins = entry['coins']
                for coin_type, coin_value in coins.items():
                    individual.append((tier, int(min_roll), int(max_roll), coin_type, coin_value))
    return individual

def process_hoard_data(data):
    """Process the hoard data into a format for database insertion."""
    hoard = []
    for table in data['hoard']:
        coins = json.dumps(table['coins'])

        tier = get_tier_from_name(table['name'])
        if tier:
            for entry in table['table']:
                # print(' ahhhha ')
                min_roll = entry.get('min')
                max_roll = entry.get('max')
                art_type, art_value = None, None
                gems_type, gems_value = None, None
                if 'artObjects' in entry:
                    art_type = entry['artObjects'].get('type')
                    art_value = entry['artObjects'].get('amount')
                if 'gems' in entry:
                    gems_type = entry['gems'].get('type')
                    gems_value = entry['gems'].get('amount')
                magic_items_type, magic_items_roll = None, None

                if isinstance(entry.get('magicItems'), list):
                    for item in entry['magicItems']:
                        magic_items_type = item.get('type')
                        magic_items_roll = item.get('amount')

                hoard.append(
                    (tier, coins, int(min_roll), int(max_roll), art_type, art_value, gems_type, gems_value, magic_items_type, magic_items_roll)
                )
    return hoard

def process_magic_items_data(data):
    """Process the magic items data into a format for database insertion."""
    magic_tables = []

    for table in data['magicItems']:
        magic_table = []
        name = table['name']

        for entry in table['table']:
            min_roll = entry['min']
            max_roll = entry['max']
            if 'item' in entry and 'choose' not in entry:
                item = entry['item']
                if '|XDMG' in item:
                    continue
                if item.startswith("{@item ") and item.endswith("}"):
                    item = item[7:-1]

            elif 'choose' in entry and 'item' not in entry:
                if 'fromGeneric' in entry['choose']:
                    item = entry['choose']['fromGeneric'][0]

                if 'fromGroup' in entry['choose']:
                    item = entry['choose']['fromGroup'][0]

                if '|XDMG' in item:
                    continue

            elif 'choose' and 'item' in entry:
                # print(entry)
                item = entry['item']
                if '|XDMG' in item:
                    continue
            else:
                print('fufidklsa')
            if '{@item ' in item:
                item = item.replace('{@item ', '')
                item = item.replace('}', '')
            magic_table.append((name, min_roll, max_roll, item))
        magic_tables.append(magic_table)
    magic_tables = [lst for lst in magic_tables if lst]
    magic_tables = [item for lst in magic_tables for item in lst]
    return magic_tables

def process_gems_data(data):
    """Process the gems data into a format for database insertion."""
    gems = []
    for table in data['gems']:
        gem_type = table['name']
        for entry in table['table']:
            if '{@item ' in entry:
                entry = entry.replace('{@item ', '').replace('}', '')
                gems.append((gem_type, entry))
    return gems

def process_art_objects_data(data):
    """Process the art objects data into a format for database insertion."""
    obje_dart = []
    for table in data['artObjects']:
        art_type = table['name']
        for entry in table['table']:
            if '{@item ' in entry:
                entry = entry.replace('{@item ', '').replace('}', '')
                obje_dart.append((art_type, entry))
    return obje_dart

def create_loot_tables(cursor):
    """Create the necessary tables in the database."""
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS loot_tables (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        cr_min INTEGER,
        cr_max INTEGER
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS magic_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        table_type TEXT NOT NULL,
        min_roll INTEGER NOT NULL,
        max_roll INTEGER NOT NULL,
        name TEXT NOT NULL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS gems (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        gem_type TEXT NOT NULL,
        name TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS art (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        art_type TEXT NOT NULL,
        name TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS hoard (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tier TEXT NOT NULL,
        coins TEXT NOT NULL,
        min_roll INTEGER NOT NULL,
        max_roll INTEGER NOT NULL,
        art_type TEXT,
        art_value TEXT,
        gems_type TEXT,
        gems_value TEXT,
        magic_items_type TEXT,
        magic_items_roll TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS individual (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tier TEXT NOT NULL,
        min_roll INTEGER NOT NULL,
        max_roll INTEGER NOT NULL,
        coin_type TEXT,
        coin_value TEXT
    )
    ''')
    
    
def create_spell_tables(cursor):
    """Create the necessary tables in the database."""
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS spells (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT NOT NULL,
        name TEXT NOT NULL,
        spell_level TEXT NOT NULL
    )
    ''')    
    
    


def insert_data(cursor, table, columns, data):
    """
    Insert the processed data into the database.
    This version accepts dynamic columns for different table structures.

    cursor: SQLite cursor object
    table: The name of the table to insert into
    columns: List of column names (e.g. ['tier', 'min_roll', 'max_roll', 'coin_type', 'coin_value'])
    data: The data to be inserted (list of tuples)
    """
    # Create a comma-separated string of column names
    column_str = ', '.join(columns)
    # Create a string of placeholders for each column
    placeholders = ', '.join(['?'] * len(columns))
    
    # Build the dynamic INSERT query
    query = f'''
    INSERT INTO {table} ({column_str})
    VALUES ({placeholders})
    '''
    
    # Execute the insert operation with the provided data
    cursor.executemany(query, data)

    
    
    

    
    
def build_spells_db():
    
    sources = ['phb', 'xge', 'tce']
    spells = []
    for source in sources:
        # print(source)
        data = load_data('data/spells-' + source + '.json')

        for key, item in data.items():
            for stuff in data[key]:
                spell_name = stuff['name']
                spell_level = stuff['level']
                spell = (source, spell_name, 'Level ' + str(spell_level))
                # print(f'{spell_name}, Level {spell_level}')
                spells.append(spell)
    
    
    with sqlite3.connect('spells.db') as conn:
        cursor = conn.cursor()

        create_spell_tables(cursor)
    
        insert_data(
            cursor, 'spells', 
            ['source', 'name', 'spell_level'], spells
        )
        conn.commit()
    
def build_loot_db():
    data = load_data('data/loot.json')

    # Connect to SQLite database (or create it if it doesn't exist)
    with sqlite3.connect('loot.db') as conn:
        cursor = conn.cursor()

        create_loot_tables(cursor)

        # Process and insert data into individual table
        individual_data = process_individual_data(data)
        insert_data(
            cursor, 'individual', 
            ['tier', 'min_roll', 'max_roll', 'coin_type', 'coin_value'], individual_data
        )

        # Process and insert data into hoard table
        hoard_data = process_hoard_data(data)
        insert_data(
            cursor, 'hoard', 
            ['tier', 'coins', 'min_roll', 'max_roll', 'art_type', 'art_value', 'gems_type', 'gems_value', 
             'magic_items_type', 'magic_items_roll'], hoard_data
        )

        # Process and insert data into magic_items table
        magic_items_data = process_magic_items_data(data)
        insert_data(
            cursor, 'magic_items', 
            ['table_type', 'min_roll', 'max_roll', 'name'], magic_items_data
        )

        # Process and insert data into gems table
        gems_data = process_gems_data(data)
        insert_data(
            cursor, 'gems', 
            ['gem_type', 'name'], gems_data
        )

        # Process and insert data into art table
        art_objects_data = process_art_objects_data(data)
        insert_data(
            cursor, 'art', 
            ['art_type', 'name'], art_objects_data
        )
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS cr_tier(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tier TEXT NOT NULL,
        min_cr INTEGER NOT NULL,
        max_cr INTEGER NOT NULL)
        ''')

        data = [
            ('Tier_1', 0, 4),
            ('Tier_2', 5, 10),
            ('Tier_3', 11, 16),
            ('Tier_4', 17, 99)
        ]

        cursor.executemany('''
        INSERT INTO cr_tier (tier, min_cr, max_cr)
        VALUES (?, ?, ?)
        ''', data)

        conn.commit()

    
    
    
    
    
    
    
    
def main():
    build_loot_db()
    build_spells_db()
    

if __name__ == "__main__":
    main()
