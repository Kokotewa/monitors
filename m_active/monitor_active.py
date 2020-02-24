"""
Active character parser for Ragnarok Online Aegis MSSQL databases.
Tracks active characters based on their last recorded position within
character.dbo.charinfo.  Character activity is tracked on a week, day,
hour, consecutive, and current (now) granularity every 'poll_interval'.
v1.0.0 Koko - 20/01/19
v2.0.0 Koko - 20/02/09
 - Increased quantity of logged metrics
 - Integrated with Prometheus
"""
import os
import logging
import time
import datetime
import pymssql
import prometheus_client

if bool(os.getenv('DEBUG')):
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
else:
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

def job_lookup(job_id):
    """
    Translates job_id into job_string.
    """
    job_dict = {
        '0': 'Novice',
        '1': 'Swordman',
        '2': 'Magician',
        '3': 'Archer',
        '4': 'Acolyte',
        '5': 'Merchant',
        '6': 'Thief',
        '7': 'Knight',
        '8': 'Priest',
        '9': 'Wizard',
        '10': 'Blacksmith',
        '11': 'Hunter',
        '12': 'Assassin',
        '13': 'Knight',  # Peco
        '14': 'Crusader',
        '15': 'Monk',
        '16': 'Sage',
        '17': 'Rogue',
        '18': 'Alchemist',
        '19': 'Bard',
        '20': 'Dancer',
        '21': 'Crusader',  # Peco
        '22': 'Wedding',
        '23': 'Super Novice',
        '24': 'Gunslinger',
        '25': 'Ninja',
        '4001': 'Novice High',
        '4002': 'Swordman High',
        '4003': 'Magician High',
        '4004': 'Archer High',
        '4005': 'Acolyte High',
        '4006': 'Merchant High',
        '4007': 'Thief High',
        '4008': 'Lord Knight',
        '4009': 'High Priest',
        '4010': 'High Wizard',
        '4011': 'Whitesmith',
        '4012': 'Sniper',
        '4013': 'Assassin Cross',
        '4014': 'Lord Knight',  # Peco
        '4015': 'Paladin',
        '4016': 'Champion',
        '4017': 'Professor',
        '4018': 'Stalker',
        '4019': 'Creator',
        '4020': 'Clown',
        '4021': 'Gypsy',
        '4022': 'Paladin',  # Peco
        '4023': 'Baby Novice',
        '4024': 'Baby Swordman',
        '4025': 'Baby Magician',
        '4026': 'Baby Archer',
        '4027': 'Baby Acolyte',
        '4028': 'Baby Merchant',
        '4029': 'Baby Thief',
        '4030': 'Baby Knight',
        '4031': 'Baby Priest',
        '4032': 'Baby Wizard',
        '4033': 'Baby Blacksmith',
        '4034': 'Baby Hunter',
        '4035': 'Baby Assassin',
        '4036': 'Baby Knight',  # Peco
        '4037': 'Baby Crusader',
        '4038': 'Baby Monk',
        '4039': 'Baby Sage',
        '4040': 'Baby Rogue',
        '4041': 'Baby Alchemist',
        '4042': 'Baby Bard',
        '4043': 'Baby Dancer',
        '4044': 'Baby Crusader',  # Peco
        '4045': 'Baby Super Novice',
        '4046': 'Taekwon',
        '4047': 'Star Gladiator',
        '4048': 'Star Gladiator',  # Union
        '4049': 'Soul Linker'
        }
    job_str = job_dict[str(job_id)]

    return job_str

def gen_charinfo_db(server, user, password, database):
    """
    Return character positions, id, and info from db charinfo table.
    """
    # Create a new connection to database
    logging.debug('Opening connection to %s', server)
    connection = pymssql.connect(
        server=server,
        user=user,
        password=password,
        database=database)

    # Perform DB query
    cursor = connection.cursor()
    cursor.callproc('rocp_admin_charinfo_db')
    cursor.nextset()
    results = cursor.fetchall()
    connection.commit()

    # Close connection
    logging.debug('Closing connection to %s', server)
    connection.close()

    # Build charinfo_db
    charinfo_db = {}
    for result in results:
        charinfo_db[result[0]] = {
            'position': {
                'mapname': result[1],
                'xPos': result[2],
                'yPos': result[3]
                },
            'id': {
                'GID': result[4],
                'AID': result[5],
                },
            'info': {
                'job': result[6],
                'base_level': result[7],
                'job_level': result[8],
                'stat_points': result[9],
                'skill_points': result[10],
                'exp': result[11],
                'jobexp': result[12],
                'money': result[13]
                }
            }

    return charinfo_db

def initialize_active(charinfo_db, gauges):
    """
    Initialize charinfo_active and mapinfo_active dictionaries.
    """
    charinfo_active = {}
    mapinfo_active = {}
    for character in charinfo_db:
        logging.info('Initializing character %s', character)
        charinfo_active[character] = {
            'position': charinfo_db[character]['position'],
            'info': charinfo_db[character]['info'],
            'id': charinfo_db[character]['id'],
            'active': {
                'week': 0,
                'day': 0,
                'hour': 0,
                'consecutive': 0,
                'now': 0
                }
            }

        # Update character info gauges
        gauges['info']['base_level'].labels(
            character=character,
            GID=charinfo_active[character]['id']['GID'],
            AID=charinfo_active[character]['id']['AID']
            ).set(charinfo_active[character]['info']['base_level'])
        gauges['info']['job_level'].labels(
            character=character,
            GID=charinfo_active[character]['id']['GID'],
            AID=charinfo_active[character]['id']['AID']
            ).set(charinfo_active[character]['info']['job_level'])
        gauges['info']['stat_points'].labels(
            character=character,
            GID=charinfo_active[character]['id']['GID'],
            AID=charinfo_active[character]['id']['AID']
            ).set(charinfo_active[character]['info']['stat_points'])
        gauges['info']['skill_points'].labels(
            character=character,
            GID=charinfo_active[character]['id']['GID'],
            AID=charinfo_active[character]['id']['AID']
            ).set(charinfo_active[character]['info']['skill_points'])
        gauges['info']['money'].labels(
            character=character,
            GID=charinfo_active[character]['id']['GID'],
            AID=charinfo_active[character]['id']['AID']
            ).set(charinfo_active[character]['info']['money'])

    return charinfo_active, mapinfo_active

def update_active(charinfo_active, mapinfo_active, charinfo_db, gauges):
    """
    Update charinfo_active and mapinfo_active dictionaries to latest character state.
    """
    for map_name in mapinfo_active:
        mapinfo_active[map_name] = 0

    for character in charinfo_db:
        try:
            # Character is active if position|info differs from last recorded position|info
            if (
                    charinfo_db[character]['position'] != charinfo_active[character]['position'] or
                    charinfo_db[character]['info'] != charinfo_active[character]['info']
                ):
                update = True
                charinfo_active[character]['position'] = charinfo_db[character]['position']
                charinfo_active[character]['info'] = charinfo_db[character]['info']
                charinfo_active[character]['active']['week'] += 1
                charinfo_active[character]['active']['day'] += 1
                charinfo_active[character]['active']['hour'] += 1
                charinfo_active[character]['active']['consecutive'] += 1
                charinfo_active[character]['active']['now'] = 1

            # Character was previously active
            elif charinfo_active[character]['active']['now'] == 1:
                update = True
                charinfo_active[character]['active']['consecutive'] = 0
                charinfo_active[character]['active']['now'] = 0
            else:
                update = False

        # Newly created characters will be absent from charinfo_active
        except KeyError:
            update = True
            logging.debug(
                'Character %s is newly created, adding to charinfo_active',
                character)
            charinfo_active[character] = {
                'position': charinfo_db[character]['position'],
                'info': charinfo_db[character]['info'],
                'id': charinfo_db[character]['id'],
                'active': {
                    'week': 0,
                    'day': 0,
                    'hour': 0,
                    'consecutive': 0,
                    'now': 0
                    }
                }

        if update is True:
            # Update mapinfo_active dictionary
            try:
                mapinfo_active[charinfo_active[character]['position']['mapname']] += 1
            except KeyError:
                logging.debug(
                    'Map %s is newly visited, adding to mapinfo_active',
                    charinfo_active[character]['position']['mapname'])
                mapinfo_active[charinfo_active[character]['position']['mapname']] = 1

            # Update character active gauge
            gauges['active']['character'].labels(
                character=character,
                GID=charinfo_active[character]['id']['GID'],
                AID=charinfo_active[character]['id']['AID']
                ).set(charinfo_active[character]['active']['now'])

            # Update character info gauges
            gauges['info']['base_level'].labels(
                character=character,
                GID=charinfo_active[character]['id']['GID'],
                AID=charinfo_active[character]['id']['AID']
                ).set(charinfo_active[character]['info']['base_level'])
            gauges['info']['job_level'].labels(
                character=character,
                GID=charinfo_active[character]['id']['GID'],
                AID=charinfo_active[character]['id']['AID']
                ).set(charinfo_active[character]['info']['job_level'])
            gauges['info']['stat_points'].labels(
                character=character,
                GID=charinfo_active[character]['id']['GID'],
                AID=charinfo_active[character]['id']['AID']
                ).set(charinfo_active[character]['info']['stat_points'])
            gauges['info']['skill_points'].labels(
                character=character,
                GID=charinfo_active[character]['id']['GID'],
                AID=charinfo_active[character]['id']['AID']
                ).set(charinfo_active[character]['info']['skill_points'])
            gauges['info']['money'].labels(
                character=character,
                GID=charinfo_active[character]['id']['GID'],
                AID=charinfo_active[character]['id']['AID']
                ).set(charinfo_active[character]['info']['money'])

            logging.info(
                '{character:25} {job:15} {location:25} blv:{base_level:3} jlv:{job_level:3} '
                'bpts:{stat_points:3} jpts:{skill_points:3} c:{consecutive:3} '
                'h:{hour:3} d:{day:3} w:{week:3}'.format(
                    character=character,
                    job=job_lookup(charinfo_active[character]['info']['job']),
                    location='{mapname} ({xPos},{yPos})'.format(
                        mapname=charinfo_active[character]['position']['mapname'],
                        xPos=charinfo_active[character]['position']['xPos'],
                        yPos=charinfo_active[character]['position']['yPos']
                        ),
                    base_level=charinfo_active[character]['info']['base_level'],
                    job_level=charinfo_active[character]['info']['job_level'],
                    stat_points=charinfo_active[character]['info']['stat_points'],
                    skill_points=charinfo_active[character]['info']['skill_points'],
                    consecutive=charinfo_active[character]['active']['consecutive'],
                    hour=charinfo_active[character]['active']['hour'],
                    day=charinfo_active[character]['active']['day'],
                    week=charinfo_active[character]['active']['week']
                    )
                )

    # Update map active gauge
    for map_name in mapinfo_active:
        gauges['active']['map'].labels(
            map_name=map_name
            ).set(mapinfo_active[map_name])

    return charinfo_active, mapinfo_active


def reset_active(charinfo_active, last_reset):
    """
    Reset charinfo_active active counters.
    """
    # Set current time
    time_now = datetime.datetime.now()

    # Reset week, day, & hour if week rollover
    if time_now - datetime.timedelta(weeks=1) > last_reset['week']:
        logging.info('Resetting week, day, and hour counters')
        last_reset['week'] = time_now
        last_reset['day'] = time_now
        last_reset['hour'] = time_now

        for character in charinfo_active:
            charinfo_active[character]['active']['week'] = 0
            charinfo_active[character]['active']['day'] = 0
            charinfo_active[character]['active']['hour'] = 0

    # Reset day & hour if day rollover
    elif time_now - datetime.timedelta(days=1) > last_reset['day']:
        logging.info('Resetting day and hour counters')
        last_reset['day'] = time_now
        last_reset['hour'] = time_now

        for character in charinfo_active:
            charinfo_active[character]['active']['day'] = 0
            charinfo_active[character]['active']['hour'] = 0

    # Reset hour if hour rollover
    elif time_now - datetime.timedelta(hours=1) > last_reset['hour']:
        logging.info('Resetting hour counter')
        last_reset['hour'] = time_now

        for character in charinfo_active:
            charinfo_active[character]['active']['hour'] = 0

    return charinfo_active, last_reset


def monitor_active(db_hostname, db_username, db_password, db_database, poll_interval):
    """
    Monitor active characters with reference to changing map positions.
    """
    # Define gauges
    gauges = {
        'active': {
            'map': prometheus_client.Gauge(
                name='character_population',
                documentation='# of active characters on map',
                labelnames=['map_name']
                ),
            'character': prometheus_client.Gauge(
                name='character_active',
                documentation='Whether the character is active',
                labelnames=['character', 'GID', 'AID']
                )
            },
        'info': {
            'base_level': prometheus_client.Gauge(
                name='character_base_level',
                documentation='Character base level',
                labelnames=['character', 'GID', 'AID']
                ),
            'job_level': prometheus_client.Gauge(
                name='character_job_level',
                documentation='Character job level',
                labelnames=['character', 'GID', 'AID']
                ),
            'stat_points': prometheus_client.Gauge(
                name='character_stat_points',
                documentation='Character unallocated stat points',
                labelnames=['character', 'GID', 'AID']
                ),
            'skill_points': prometheus_client.Gauge(
                name='character_skill_points',
                documentation='Character unallocated skill points',
                labelnames=['character', 'GID', 'AID']
                ),
            'money': prometheus_client.Gauge(
                name='character_money',
                documentation='Character money',
                labelnames=['character', 'GID', 'AID']
                )
            }
        }

    # Set reset rollover timestamps, last monday, midnight, last hour
    time_now = datetime.datetime.now()
    last_reset = {
        'week': time_now - datetime.timedelta(days=time_now.weekday()),
        'day': time_now.replace(hour=0, minute=0, second=0, microsecond=0),
        'hour': time_now.replace(minute=0, second=0, microsecond=0)
        }

    # Initialize charinfo_active and mapinfo_active dictionaries
    charinfo_db = gen_charinfo_db(
        server=db_hostname,
        user=db_username,
        password=db_password,
        database=db_database)
    charinfo_active, mapinfo_active = initialize_active(charinfo_db=charinfo_db, gauges=gauges)
    time.sleep(poll_interval)

    # Begin monitor loop
    while True:
        # Generate new charinfo from database
        charinfo_db = gen_charinfo_db(
            server=db_hostname,
            user=db_username,
            password=db_password,
            database=db_database)

        # Update active characters
        charinfo_active, mapinfo_active = update_active(
            charinfo_active=charinfo_active,
            mapinfo_active=mapinfo_active,
            charinfo_db=charinfo_db,
            gauges=gauges)

        # Prepare for next iteration
        charinfo_active, last_reset = reset_active(
            charinfo_active=charinfo_active,
            last_reset=last_reset)
        logging.info('Iteration complete, sleeping %s seconds', poll_interval)
        time.sleep(poll_interval)


if __name__ == '__main__':
    POLL_INTERVAL = int(os.getenv('POLL_INTERVAL'))
    PROMETHEUS_PORT = int(os.getenv('PROMETHEUS_PORT'))
    DB_HOSTNAME = str(os.getenv('DB_HOSTNAME'))
    DB_DATABASE = str(os.getenv('DB_DATABASE'))
    DB_USERNAME = str(os.getenv('DB_USERNAME'))
    DB_PASSWORD = str(os.getenv('DB_PASSWORD', 'False'))

    if DB_PASSWORD == 'False':
        logging.info('DB_PASSWORD environment variable is not set, reading from secret')
        DB_PASSWORD = open('/run/secrets/DB_PASSWORD').read()

    prometheus_client.start_http_server(PROMETHEUS_PORT)

    monitor_active(
        db_hostname=DB_HOSTNAME,
        db_username=DB_USERNAME,
        db_password=DB_PASSWORD,
        db_database=DB_DATABASE,
        poll_interval=POLL_INTERVAL)
