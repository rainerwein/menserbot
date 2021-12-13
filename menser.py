import datetime
import re
import xml.etree.ElementTree as ET
from discord.role import R
import requests

refs_regex = re.compile('(\([ ,a-zA-Z0-9]*\))')
split_refs_regex = re.compile('[\(,]([ a-zA-Z0-9]*)')
remove_refs_regex = re.compile('\([ ,a-zA-Z0-9]*\)')

def get_german_days(day_en: str) -> str:
    if day_en == 'Monday':
        return 'Montag'
    elif day_en == 'Tuesday':
        return 'Dienstag'
    elif day_en == 'Wednesday':
        return 'Mittwoch'
    elif day_en == 'Thursday':
        return 'Donnerstag'
    elif day_en == 'Friday':
        return 'Freitag'
    elif day_en == 'Saturday':
        return 'Samstag'
    elif day_en == 'Sunday':
        return 'Sonntag'
    else:
        return day_en


def get_food_types(piktogramme):
    fs = piktogramme
    food_types = []
    if fs is None:
        food_types.append('Sonstiges')
        return food_types
    if '/S.png' in fs:
        food_types.append('Schwein')
    if '/R.png' in fs:
        food_types.append('Rind')
    if '/G.png' in fs:
        food_types.append('Geflügel')
    if '/L.png' in fs:
        food_types.append('Lamm')
    if '/W.png' in fs:
        food_types.append('Wild')
    if '/F.png' in fs:
        food_types.append('Fisch')
    if '/V.png' in fs:
        food_types.append('Vegetarisch')
    if '/veg.png' in fs:
        food_types.append('Vegan')
    if '/MSC.png' in fs:
        food_types.append('MSC Fisch')
    if '/Gf.png' in fs:
        food_types.append('Glutenfrei')
    if '/CO2.png' in fs:
        food_types.append('CO2-Neutral')
    if '/B.png' in fs:
        food_types.append('Bio')
    if '/MV.png' in fs:
        food_types.append('MensaVital')
    
    return food_types


def get_refs(title):
    raw = ''.join(refs_regex.findall(title))
    return split_refs_regex.findall(raw)


def build_notes_string(title):
    food_is = []
    food_contains = []
    refs = get_refs(title)
    for r in refs:
        #Zusatzstoffe
        if r == '1':
            food_is.append('mit Farbstoff')
        elif r == '2':
            food_is.append('mit Koffein')
        elif r == '4':
            food_is.append('mit Konservierungsstoffen')
        elif r == '5':
            food_is.append('mit Süßungsmittel')
        elif r == '7':
            food_is.append('mit Antioxidationsmittel')
        elif r == '8':
            food_is.append('mit Geschmacksverstärker')
        elif r == '9':
            food_is.append('geschwefelt')
        elif r == '10':
            food_is.append('geschwärzt')
        elif r == '11':
            food_is.append('gewachst')
        elif r == '12':
            food_is.append('mit Phosphat')
        elif r == '13':
            food_is.append('mit einer Phenylalaninquelle')
        elif r == '30':
            food_is.append('mit Fettglasur')

        #Allergene
        elif r == 'Wz':
            food_contains.append('Weizen (Gluten)')
        elif r == 'Ro':
            food_contains.append('Roggen (Gluten)')
        elif r == 'Ge':
            food_contains.append('Gerste (Gluten)')
        elif r == 'Hf':
            food_contains.append('Hafer')
        elif r == 'Kr':
            food_contains.append('Krebstiere')
        elif r == 'Ei':
            food_contains.append('Eier')
        elif r == 'Er':
            food_contains.append('Erdnüsse')
        elif r == 'So':
            food_contains.append('Soja')
        elif r == 'Mi':
            food_contains.append('Milch/Laktose')
        elif r == 'Man':
            food_contains.append('Mandeln')
        elif r == 'Hs':
            food_contains.append('Haselnüsse')
        elif r == 'Wa':
            food_contains.append('Walnüsse')
        elif r == 'Ka':
            food_contains.append('Cashewnüsse')
        elif r == 'Pe':
            food_contains.append('Pekanüsse')
        elif r == 'Pa':
            food_contains.append('Paranüsse')
        elif r == 'Pi':
            food_contains.append('Pistazien')
        elif r == 'Mac':
            food_contains.append('Macadamianüsse')
        elif r == 'Sel':
            food_contains.append('Sellerie')
        elif r == 'Sen':
            food_contains.append('Senf')
        elif r == 'Ses':
            food_contains.append('Sesam')
        elif r == 'Su':
            food_contains.append('Schwefeloxid/Sulfite')
        elif r == 'Lu':
            food_contains.append('Lupinen')
        elif r == 'We':
            food_contains.append('Weichtiere')
        else:
            food_contains.append('mit undefinierter Chemikalie ' + r)
    return food_contains


def get_description(title):
    raw = remove_refs_regex.split(title)
    return ''.join(raw)


def parse_url(url, mensa):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0',
    }

    xml_data = requests.get(url, headers=headers);

    if not xml_data.ok:
        print(f'Error: {xml_data.status_code}. check mensa parameter')
        return

    root = ET.fromstring(xml_data.content.decode('utf-8'))

    menu = ''

    for day in root:
        date = datetime.date.fromtimestamp(int(day.get('timestamp')))
        today = datetime.date.today()
        if date < today:
            continue

        if date == today:
            daystring = 'Heute'
        elif today + datetime.timedelta(days=1) == date:
            daystring = 'Morgen'
        else:
            daystring = get_german_days(date.strftime('%A'))
        fullstring = date.strftime(f'{daystring} %d.%m.%Y')
        menu += f'\n{fullstring}\n'
        for item in day:
            title = item.find('title').text
            description = get_description(title)
            category = item.find('category').text
            notes = build_notes_string(title)
            plist = [item.find('preis1').text,
                     item.find('preis2').text,
                     item.find('preis3').text]
            food_type = get_food_types(item.find('piktogramme').text)
            if 'Vegan' in food_type or 'Vegetarisch' in food_type:
                menu += f'{description}\n'

    return menu
        
        