# Web API: Plattenanalyse

Mit dieser API kannst du Bilder von Referenz- und Experimentplatten analysieren und Ergebnisse wie Daten und Highlights der Platten erhalten.

## Server starten

Um den Server zu starten, benutze den folgenden Befehl:

```bash
python Web_API.py --host 0.0.0.0 --port 5000
```

- `--host`: Die IP-Adresse, unter der der Server erreichbar ist. Standard: `0.0.0.0` (zugänglich von überall im Netzwerk).
- `--port`: Der Port, auf dem der Server lauscht. Standard: `5000`.

## Anfragen an die API stellen

Du kannst Anfragen an die API senden, z. B. mit folgendem Python-Skript:

```python 
import requests

# URL der API
url = "http://localhost:5000/process"

# Daten für die Anfrage
data = {
    "reference": "data/A_ref.JPG",  # Pfad zur Referenzplatte
    "experiment": "data/A_exp.JPG"  # Pfad zur Experimentplatte
}

# Anfrage senden
response = requests.post(url, json=data)

# Ergebnisse prüfen
if response.status_code == 200:
    result = response.json()
    print("Daten:", result["data"])
    print("Verfügbare Bilder:", result["images"].keys())
else:
    print("Fehler:", response.status_code, response.text)

```

### Testskript
Ein Beispiel für eine Anfrage findest du im Skript `Web_API_request.py`.

Passe den Datenpfad in der Datei an oder lege die Dateien in den entsprechenden Ordner mit den Namen `A_ref.JPG` und `A_exp.JPG`.
Führe das Skript aus, um eine Anfrage an die API zu senden und die Ergebnisse zu testen.

### API Response
Die API gibt eine JSON-Antwort zurück, die zwei Hauptbereiche enthält:

- `data`: Analysedaten der Platten.
- `images`: Base64-kodierte Bilder mit den Ergebnissen.

#### Verfügbare Bilder
- `reference_plate`: Originalbild der Referenzplatte.
- `experiment_plate`: Originalbild der Experimentplatte.
- `normalized_plate`: Normalisierte Experimentplatte.
- `highlights_absolute`: Highlights des ersten Experiments (absolute Größe/Interaktion).
- `highlights_difference`: Highlights des zweiten Experiments (Größenunterschied zwischen Reihe A und B).
- `highlights_both`: Kombination der Highlights aus beiden Experimenten.

### Wichtiger Hinweis
Die Highlight-Bilder sollten immer in Kombination mit der Referenz- oder Experimentplatte verwendet werden, da sie allein keine vollständige Information über gewachsene Zellen enthalten.


## Auswertung

Ob der Unterschied zwischen Reihe A und B signifikant ist, steht in `result["data"]["Exp2: Significant Difference"]` (wird abgeleitet aus `result["data"]["Exp2: P-Value"]`). Die Stärke des Effekts steht in `result["data"]["Exp2: Effect Size"]`