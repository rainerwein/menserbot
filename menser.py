import datetime
import re
import xml.etree.ElementTree as ET
from discord.role import R
import aiohttp
import helper

refs_regex = re.compile('(\([ ,a-zA-Z0-9]*\))')
split_refs_regex = re.compile('[\(,]([ a-zA-Z0-9]*)')
remove_refs_regex = re.compile('\([ ,a-zA-Z0-9]*\)')

class Plan:
    def __init__(self, mensa, veggie):
        self.mensa = mensa
        self.veggie = veggie
        self.days = []
    
    def add_day(self, day):
        self.days.append(day)
        return day

    class Day :
        def __init__(self, day):
            self.day = day
            self.meals: list[str] = []
        
        def add_meal(self, meal: str):
            self.meals.append(meal)


def get_german_day(day_en: str) -> str:
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
    food_types_emoji = []
    if fs is None:
        food_types.append('Sonstiges')
        return food_types, food_types_emoji
    if '/S.png' in fs:
        food_types.append('Schwein')
        food_types_emoji.append('🐷')
    if '/R.png' in fs:
        food_types.append('Rind')
        food_types_emoji.append('🐮')
    if '/G.png' in fs:
        food_types.append('Geflügel')
        food_types_emoji.append('🐔')
    if '/L.png' in fs:
        food_types.append('Lamm')
        food_types_emoji.append('🐑')
    if '/W.png' in fs:
        food_types.append('Wild')
        food_types_emoji.append('🐈')
    if '/F.png' in fs:
        food_types.append('Fisch')
        food_types_emoji.append('🐟')
    if '/V.png' in fs:
        food_types.append('Vegetarisch')
        food_types_emoji.append('🥕')
    if '/veg.png' in fs:
        food_types.append('Vegan')
        food_types_emoji.append('🌱')
    if '/MSC.png' in fs:
        food_types.append('MSC Fisch')
        food_types_emoji.append('🐟')
    if '/Gf.png' in fs:
        food_types.append('Glutenfrei')
    if '/CO2.png' in fs:
        food_types.append('CO2-Neutral')
    if '/B.png' in fs:
        food_types.append('Bio')
    if '/MV.png' in fs:
        food_types.append('MensaVital')
    
    #remove duplicates from emoji list
    return food_types, list(dict.fromkeys(food_types_emoji))


def build_notes_string(title):
    food_is = []
    food_contains = []
    refs = split_refs_regex.findall(''.join(refs_regex.findall(title)))
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
    return re.sub(' +', ' ', ''.join(remove_refs_regex.split(title))).strip()


async def get_plan(mensa, veggie: bool) -> Plan:
    # headers = {
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0',
    # }
    url = helper.api_url(mensa)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if not response.status == 200:
                    return

                xml_data = await response.text()
    except Exception as e:
        print(e)
        return

    root = ET.fromstring(xml_data)
    
    plan = Plan(mensa, veggie)

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
            daystring = get_german_day(date.strftime('%A'))

        daystring = date.strftime(f'{daystring} %d.%m.%Y')

        added_items = []
        # meals = []

        planday = plan.add_day(Plan.Day(daystring))

        for item in day:
            title = item.find('title').text
            description = get_description(title)
            # line = item.find('category').text
            # notes = build_notes_string(title)
            plist = [item.find('preis1').text, # Studierende
                     item.find('preis2').text, # Bedienstete
                     item.find('preis3').text] # Gäste
            if description in added_items:
                continue
            food_type, food_type_emoji = get_food_types(item.find('piktogramme').text)
            if not veggie or 'Vegan' in food_type or 'Vegetarisch' in food_type:
                emoji_string = f'`{"".join(food_type_emoji)}`' if food_type_emoji else ''
                price_string = f'`{plist[0]}€`' if not plist[0] == '-' else ''
                menustring = f'{emoji_string}  {description}  {price_string}\n'

                added_items.append(description)
                planday.add_meal(menustring)
    return plan
