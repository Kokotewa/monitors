"""
Itemlog parser for Ragnarok Online Aegis MSSQL databases.
Tracks character itemlog activity with reference to action type
itemlog.dbo.itemlog.  Character itemlog activity is tracked on a week, day,
hour, consecutive, and current (now) granularity every 'poll_interval'.
v1.0.0 Koko - 20/05/27
"""
import os
import logging
import time
import datetime
import pyodbc
import prometheus_client

if bool(os.getenv('DEBUG')):
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
else:
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)


def gen_itemlog_db(server, username, password, database, action_keys, poll_interval):
    """
    Return character itemlog activity from ItemLog table.
    """
    # Create a new connection to database
    logging.debug('Opening connection to %s', server)
    connection = pyodbc.connect(
        'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'.format(
            driver='{ODBC Driver 17 for SQL Server}',
            server=server,
            database=database,
            username=username,
            password=password
            )
        )

    # Perform DB query
    try: 
        cursor = connection.cursor()
        cursor.execute('EXEC rocp_admin_itemlog_db @pollinterval = ?', poll_interval)
        results = cursor.fetchall()
    except pyodbc.OperationalError:
        logging.info('No itemlog updates in the last interval')
        results = []

    # Close connection
    logging.debug('Closing connection to %s', server)
    connection.close()

    # Build itemlog_db
    itemlog_db = {}
    for result in results:
        try:
            # Attempt to increment action counter
            itemlog_db[result[0]]['action'][result[3]] += 1
        except KeyError:
            # Initialize character in itemlog_db
            itemlog_db[result[0]] = {
                'id': {
                    'GID': result[1],
                    'AID': result[2]
                    },
                'action': {}
                }

            # Initialize action counters
            for action in action_keys:
                itemlog_db[result[0]]['action'][action] = 0

            # Increment action counter
            itemlog_db[result[0]]['action'][result[3]] += 1

    return itemlog_db


def update_active(itemlog_active, itemlog_db, gauges, action_keys):
    """
    Update itemlog_active dictionaries to latest itemlog counters.
    """
    # Create itemlog_active keys for new characters
    characters_new = itemlog_db.keys() - itemlog_active.keys()
    for character in characters_new:
        logging.info('Character %s is new, adding to itemlog_active', character)
        itemlog_active[character] = {
            'id': itemlog_db[character]['id'],
            'action': {}
            }
        for action in action_keys:
            itemlog_active[character]['action'][action] = {
                'week': 0,
                'day': 0,
                'hour': 0,
                'consecutive': 0,
                'now': 0
                }

    # Update itemlog_active state and gauges
    for character in itemlog_active:
        # Itemlog character is active if character has entries in itemlog_db
        if character in itemlog_db:
            for action in itemlog_active[character]['action']:
                for counter in ['week', 'day', 'hour', 'consecutive', 'now']:
                    itemlog_active[character]['action'][action][counter] += itemlog_db[character]['action'][action]

                if itemlog_active[character]['action'][action]['now'] != 0:
                    logging.info(
                        '{character:25} {action:20} c:{consecutive:3} h:{hour:3} d:{day:3} w:{week:3}'.format(
                            character=character,
                            action=gauges[action]._name,
                            consecutive=itemlog_active[character]['action'][action]['consecutive'],
                            hour=itemlog_active[character]['action'][action]['hour'],
                            day=itemlog_active[character]['action'][action]['day'],
                            week=itemlog_active[character]['action'][action]['week']
                            )
                        )
        # Set consecutive and new gauges to 0 for inactive characters
        else:
            for action in itemlog_active[character]['action']:
                for counter in ['consecutive', 'now']:
                    itemlog_active[character]['action'][action][counter] = 0

        # Update itemlog gauges
        for action in action_keys:
            gauges[action].labels(
                character=character
                ).set(itemlog_active[character]['action'][action]['now'])

    return itemlog_active


def reset_active(itemlog_active, last_reset, action_keys):
    """
    Reset itemlog_active active counters.
    """
    # Set current time
    time_now = datetime.datetime.now()

    # Reset week, day, & hour if week rollover
    if time_now - datetime.timedelta(weeks=1) > last_reset['week']:
        logging.info('Resetting week, day, and hour counters')
        last_reset['week'] = time_now
        last_reset['day'] = time_now
        last_reset['hour'] = time_now

        for character in itemlog_active:
            for action in action_keys:
                itemlog_active[character]['action'][action]['week'] = 0
                itemlog_active[character]['action'][action]['day'] = 0
                itemlog_active[character]['action'][action]['hour'] = 0

    # Reset day & hour if day rollover
    elif time_now - datetime.timedelta(days=1) > last_reset['day']:
        logging.info('Resetting day and hour counters')
        last_reset['day'] = time_now
        last_reset['hour'] = time_now

        for character in itemlog_active:
            for action in action_keys:
                itemlog_active[character]['action'][action]['day'] = 0
                itemlog_active[character]['action'][action]['hour'] = 0

    # Reset hour if hour rollover
    elif time_now - datetime.timedelta(hours=1) > last_reset['hour']:
        logging.info('Resetting hour counter')
        last_reset['hour'] = time_now

        for character in itemlog_active:
            for action in action_keys:
                itemlog_active[character]['action'][action]['hour'] = 0

    return itemlog_active, last_reset


def monitor_itemlog(db_hostname, db_username, db_password, db_database, poll_interval):
    """
    Monitor active characters with reference to changing map positions.
    """
    # Define gauges
    gauges = {
        0: prometheus_client.Gauge(
            name='item_drop',
            documentation='Items removed by character drop',
            labelnames=['character']
            ),
        1: prometheus_client.Gauge(
            name='item_pickup',
            documentation='Items created by character pickup',
            labelnames=['character']
            ),
        2: prometheus_client.Gauge(
            name='item_consumed',
            documentation='Items consumed by character',
            labelnames=['character']
            ),
        3: prometheus_client.Gauge(
            name='item_traded',
            documentation='Items traded between characters',
            labelnames=['character']
            ),
        4: prometheus_client.Gauge(
            name='item_bought_pc',
            documentation='Items moved by purchase from PC',
            labelnames=['character']
            ),
        5: prometheus_client.Gauge(
            name='item_bought_npc',
            documentation='Items created by purchase from NPC',
            labelnames=['character']
            ),
        6: prometheus_client.Gauge(
            name='item_sold_npc',
            documentation='Items consumed by sell to NPC',
            labelnames=['character']
            ),
        7: prometheus_client.Gauge(
            name='item_mvp',
            documentation='Items created by MVP rewards',
            labelnames=['character']
            ),
        8: prometheus_client.Gauge(
            name='item_stolen',
            documentation='Items created by steal',
            labelnames=['character']
            ),
        9: prometheus_client.Gauge(
            name='item_misc_1',
            documentation='Items consumed by misc_1 e.g. endow skills, pet capture, etc.',
            labelnames=['character']
            ),
        10: prometheus_client.Gauge(
            name='item_misc_2',
            documentation='N/A',
            labelnames=['character']
            ),
        11: prometheus_client.Gauge(
            name='item_npc_compulsive',
            documentation='Items created by compulsive NPCs',
            labelnames=['character']
            ),
        12: prometheus_client.Gauge(
            name='item_npc_event',
            documentation='Items created by event NPCs',
            labelnames=['character']
            ),
        13: prometheus_client.Gauge(
            name='item_gm',
            documentation='Items created by GMs using /item',
            labelnames=['character']
            ),
        14: prometheus_client.Gauge(
            name='item_box',
            documentation='Items created by OCAs, OPBs, OBBs, etc.',
            labelnames=['character']
            ),
        15: prometheus_client.Gauge(
            name='item_blacksmith',
            documentation='Items created by Blacksmiths',
            labelnames=['character']
            ),
        16: prometheus_client.Gauge(
            name='item_npc_give',
            documentation='Items created by NPC e.g. quest',
            labelnames=['character']
            ),
        17: prometheus_client.Gauge(
            name='item_npc_take',
            documentation='Items consumed by NPC e.g. quest, refine, etc.',
            labelnames=['character']
            ),
        18: prometheus_client.Gauge(
            name='zeny_npc',
            documentation='Zeny consumed/created by NPC',
            labelnames=['character']
            ),
        19: prometheus_client.Gauge(
            name='item_inv_to_kafra',
            documentation='Items moved to Kafra storage from character inventory',
            labelnames=['character']
            ),
        20: prometheus_client.Gauge(
            name='item_inv_to_cart',
            documentation='Items moved to Cart from character inventory',
            labelnames=['character']
            ),
        21: prometheus_client.Gauge(
            name='item_kafra_to_inv',
            documentation='Items moved to character inventory from Kafra storage',
            labelnames=['character']
            ),
        22: prometheus_client.Gauge(
            name='item_kafra_to_cart',
            documentation='Items moved to Kafra storage from character cart',
            labelnames=['character']
            ),
        23: prometheus_client.Gauge(
            name='item_cart_to_inv',
            documentation='Items moved to character cart from character inventory money',
            labelnames=['character']
            ),
        24: prometheus_client.Gauge(
            name='item_cart_to_kafra',
            documentation='Items moved to character cart from Kafra storage',
            labelnames=['character']
            ),
        35: prometheus_client.Gauge(
            name='item_cash_buy',
            documentation='Items created by purchase from cashshop NPC',
            labelnames=['character']
            ),
        36: prometheus_client.Gauge(
            name='item_cash_box',
            documentation='Items created by a cashshop box',
            labelnames=['character']
            )
        }

    # Set reset rollover timestamps, last monday, midnight, last hour
    time_now = datetime.datetime.now()
    last_reset = {
        'week': time_now - datetime.timedelta(days=time_now.weekday()),
        'day': time_now.replace(hour=0, minute=0, second=0, microsecond=0),
        'hour': time_now.replace(minute=0, second=0, microsecond=0)
        }

    # Initalize itemlog_active
    itemlog_active = {}

    # Begin monitor loop
    while True:
        # Generate new itemlog_db from database
        itemlog_db = gen_itemlog_db(
            server=db_hostname,
            username=db_username,
            password=db_password,
            database=db_database,
            action_keys=gauges.keys(),
            poll_interval=poll_interval
            )

        # Update itemlog_active characters
        itemlog_active = update_active(
            itemlog_active=itemlog_active,
            itemlog_db=itemlog_db,
            gauges=gauges,
            action_keys=gauges.keys()
            )

        # Prepare for next iteration
        itemlog_active, last_reset = reset_active(
            itemlog_active=itemlog_active,
            last_reset=last_reset,
            action_keys=gauges.keys()
            )

        logging.info('Iteration complete, sleeping %s seconds', poll_interval)
        time.sleep(poll_interval)


if __name__ == '__main__':
    POLL_INTERVAL = int(os.getenv('POLL_INTERVAL'))
    PROMETHEUS_PORT = int(os.getenv('PROMETHEUS_PORT'))
    DB_HOSTNAME = str(os.getenv('DB_HOSTNAME'))
    DB_DATABASE = str(os.getenv('DB_DATABASE'))
    DB_USERNAME = str(os.getenv('DB_USERNAME'))
    DB_PASSWORD = open('/run/secrets/DB_PASSWORD').read()

    prometheus_client.start_http_server(PROMETHEUS_PORT)
    monitor_itemlog(
        db_hostname=DB_HOSTNAME,
        db_username=DB_USERNAME,
        db_password=DB_PASSWORD,
        db_database=DB_DATABASE,
        poll_interval=POLL_INTERVAL
        )

