# MenserBot
## Discord Bot für die Mensen des Studentenwerks Erlangen-Nürnberg

## Wie verwenden
1. Eine Discord Application erstellen und einen Bot hinzufügen: [Discord Developer Portal](https://discordapp.com/developers/applications)
2. Den Bot token in `TOKEN_MENSERBOT` als Umgebungsvariable speichern: `export TOKEN_MENSERBOT=*yourbottoken*`
3. Einen OAuth2 Link mit `application.commands` Scope Erstellen und den Bot zum Server der Wahl hinzufügen
4. Abhängigkeiten installieren 
```
python3 -m pip install -r requirements.txt
```
5. Loslegen 
```
python3 menserbot.py
```

## Wie funktionieren
Der Bot stellt den Application command `/mensa` zur Verfügung, mit dem ein sich automatisch aktualisierender Speiseplan generiert wird.

Als Parameter lassen sich aus einer Liste die gewünschte Mensa, sowie die Option nur vegetarische / vegane Gerichte anzuzeigen, auswählen.

Zum Löschen einer Nachricht des Bots gibt es den Befehl `/löschen` der die ID (Rechtsklick -> ID kopieren) der zu löschenden Nachricht übergeben bekommt.

## Anforderungen
- Mindestens Python 3.8