## Wahlzettelgenerator für den StuRa Heidelberg

Kandidaturen auf vom StuRa zu wählende Ämter werden zzt einfach in einer DB gespeichert. Mit dieser Webapp können auf Basis der Daten auch Stimmzettel und Berichtsvorlagen nach der Wahlordnung generiert werden. Das passiert mit reinem Lesezugang zur Bewerbungsdatenbank. Es werden keine Daten zwischendurch selbst erstellt oder gespeichert.

### Lokal einrichten
Nach dem clonen muss zuerst im Ordner `maulwurf` eine Datei `.env` erstellt werden, aus der Einstellungen ausgelesen werden. Diese Datei wird nicht von git getrackt, da sie das db-Passwort erhält. Format:

```
SECRET_KEY = "Beispielschluessel"
DEBUG = 'True'
DBKEY = '.'
```

Wenn `DEBUG = 'False'` gesetzt ist, wird mit einer (am anfang leeren) SQL-Lite datei gearbeitet, dafür einmal `migrate` laufen lassen. Dann können Kandidaturen über die Adminschnittstelle mit selbst erstelltem superuser angelegt werden. Der `DBKEY` wird dabei nicht verwendet.

### Tatsächlich einrichten
Wie oben, aber mit `DEBUG = 'False'` und in der `settings.py` eingestelltem Benutzernamen zum `DBKEY`. Die Docker-Files und Compose-Anleitungen wurden von Felix Joeken geschrieben. Alle erforderlichen Pakete sollten in der `requirements.txt` sein, bis auf `gunicorn`. Mit den hier gelieferten `docker-compose`-Plänen wird vor `gunicorn` ein `nginx`-Proxy geschaltet. Static-Files werden mit dem `whitenoise`-Paket gemanagt.

### Datenschutzrelevantes
Es werden keine Daten vom Benutzer erhoben, bis auf technisch absolut notwendige cookies (CSRF-Schutz). Die Daten, die angezeigt werden, stehen schon genau so in der Datenbank. Sensible Daten wie Bewerbungsschreiben, Kontaktdaten und Matrikelnummer werden im Interface nicht angezeigt und sollten dem System a priori nicht zugänglich sein.
