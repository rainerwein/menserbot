# MenserBot
## Discord Bot für die Mensen des Studentenwerks Erlangen-Nürnberg

## Wie verwenden
1. Eine Discord Application erstellen und einen Bot hinzufügen: [Discord Developer Portal](https://discordapp.com/developers/applications)
2. Den Bot token in `TOKEN_MENSERBOT` als Umgebungsvariable speichern: `export TOKEN_MENSERBOT=<deintoken>`
3. Einen OAuth2 Link mit `application.commands` Scope Erstellen und den Bot zum Server der Wahl hinzufügen
4. Abhängigkeiten installieren 
```
python3 -m pip install -r requirements.txt
```
5. Loslegen 
```
python3 menserbot.py
```
Hinweis: Es kann bis zu einer Stunde dauern bis die slash commands bei einem neuen Bot global registriert sind.

### Alternativ kann der Bot auch über folgenden Link eingeladen werden
[HER DAMIT](https://discord.com/api/oauth2/authorize?client_id=917930384740712500&permissions=0&scope=bot%20applications.commands)

## Wie funktionieren
Der Bot stellt den Application command `/mensa` zur Verfügung, mit dem ein sich automatisch aktualisierender Speiseplan generiert wird.

Als Parameter lassen sich aus einer Liste die gewünschte Mensa, sowie die Option nur vegetarische / vegane Gerichte anzuzeigen, auswählen.

Zum Löschen einer Nachricht des Bots gibt es den Befehl `/löschen` der die ID (Rechtsklick -> ID kopieren) der zu löschenden Nachricht übergeben bekommt.

## Docker dir einen
Der Bot lässt sich mit einem der beiden Dockerfiles in ein Docker Image pflanzen um ihn in einem Container laufen zu lassen

`docker build -t menserbot -f Dockerfile.minimal`

`docker run --env TOKEN_MENSERBOT=<deintoken> menserbot:latest`

## Anforderungen
- Mindestens Python 3.8
