# MenserBot
## Discord Bot für die Mensen des Studentenwerks Erlangen-Nürnberg

## Wie verwenden
1. Eine Discord Application erstellen und einen Bot hinzufügen:[Discord Developer Portal](https://discordapp.com/developers/applications)
2. Den Bot token in [config.py](config.py) als `TOKEN_MENSERBOT` speichern
3. Einen OAuth2 Link mit `application.commands` Scope Erstellen und den Bot zum Server der Wahl hinzufügen
4. Die Guild ID in [config.py](config.py) zur Liste der `DEBUG_GUILDS` hinzufügen (Um den slash_command zu registrieren) 
5. Abhängigkeiten installieren 
```
python3 -m pip install -r requirements.txt
```
6. Loslegen 
```
python3 menserbot.py
```

## Wie funktionieren
Der Bot stellt den Application command `/mensa` zur Verfügung, mit dem ein sich automatisch aktualisierender Speiseplan generiert wird.

Als Parameter lassen sich aus einer Liste die gewünschte Mensa, sowie die Option nur vegetarische / vegane Gerichte anzuzeigen, auswählen.


## Anforderungen
- Mindestens Python 3.8