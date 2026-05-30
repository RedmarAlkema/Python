# Cosmic Confrontation

PyGame-uitwerking van de Python-eindopdracht.

## Starten

Sluit na het aanpassen/installeren van Python eerst PowerShell en VS Code volledig af
en open daarna een nieuwe terminal. Controleer dan of `python` naar Python 3.12 wijst:

```powershell
python --version
```

Voor dit project moet dit bij voorkeur `Python 3.12.x` tonen. Installeer daarna
PyGame:

```powershell
python -m pip install -r requirements.txt
```

Start het spel:

```powershell
python main.py
```

## Problemen met Python

Als `python --version` Python 3.14 toont, staat de verkeerde Python-versie vooraan
in PATH. Gebruik dan tijdelijk expliciet je Python 3.12-pad:

```powershell
& "$env:LOCALAPPDATA\Python\pythoncore-3.12-64\python.exe" --version
```

Daarmee kun je ook installeren en starten:

```powershell
& "$env:LOCALAPPDATA\Python\pythoncore-3.12-64\python.exe" -m pip install -r requirements.txt
& "$env:LOCALAPPDATA\Python\pythoncore-3.12-64\python.exe" main.py
```

Als `pip` ontbreekt:

```powershell
python -m ensurepip --upgrade
python -m pip install -r requirements.txt
```

Als `python` helemaal niet werkt, probeer dan de Python launcher:

```powershell
py -V
py list
```

Zie je alleen uitleg van de Python Install Manager en nog geen versie? Installeer dan
een runtime met:

```powershell
py install 3.12
```

Als je meerdere Python-versies hebt, kun je ook expliciet Python 3.12 gebruiken:

```powershell
py -3.12 -m pip install -r requirements.txt
py -3.12 main.py
```

## Besturing

- Pijltjes links/rechts in het startscherm: kies bordgrootte tussen 8x8 en 16x16.
- Enter of spatie: start het spel.
- Linkermuisknop op eigen bord: selecteer een schip.
- `A`: aanvalmodus, klik op het vijandelijke bord.
- `P`: speciale kracht, selecteer eerst een eigen schip en klik daarna op het juiste bord.
- `M`: bewegingsmodus, selecteer een eigen schip en gebruik de pijltjestoetsen.
- `O`: wissel de richting van de salvo-aanval.
- `R`: herstart met dezelfde bordgrootte.

## Opbouw

- `models.py`: kleine modelklassen voor bord, vloot, schepen, zichtbaarheid en asteroiden.
- `ai.py`: eenvoudige AI-keuzes.
- `main.py`: PyGame-scherm, input en beurtverloop.

De classes zijn bewust compact gehouden. `Board` koppelt de onderdelen aan elkaar,
terwijl `Fleet`, `Visibility`, `AsteroidField`, `Ship` en `Asteroid` elk een eigen
verantwoordelijkheid hebben. Regels zoals aanvallen, scannen, bewegen, gebieden
bepalen en meerdere vakjes raken zijn als herbruikbare methodes/functies opgezet.
