## Wahlzettelgenerator für den StuRa Heidelberg

Kandidaturen auf vom StuRa zu wählende Ämter werden zzt einfach in einer DB gespeichert. Mit dieser Webapp können auf Basis der Daten auch Stimmzettel generiert werden. Zur zeit zieht die App ihre Infos von einer Dummydatenbank.

### Lokal einrichten
Nach dem clonen muss zuerst im Ordner `Zettel` eine Datei `.env` erstellt werden, aus der Einstellungen ausgelesen werden. Diese Datei wird nicht von git getrackt, da sie das db-Passwort erhält. Format:

```
SECRET_KEY = "Beispielschluessel"
DEBUG = 'True'
DBKEY = '.'
```

Wenn `DEBUG = 'False'` gesetzt ist, wird mit einer (am anfang leeren) SQL-Lite datei gearbeitet, dafür einmal `migrate` laufen lassen. Dann können Kandidaturen über die Adminschnittstelle mit selbst erstelltem superuser angelegt werden. Der `DBKEY` wird dabei nicht verwendet.

### Tatsächlich einrichten
Wie oben, aber mit `DEBUG = 'False'` und in der `settings.py` eingestelltem Benutzernamen zum `DBKEY`.
