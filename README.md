# Cosmic Confrontation

Pygame-uitwerking van de Python-eindopdracht: een Battleship-achtig ruimtespel met
schepen, speciale krachten, asteroiden, AI, opgeslagen spellen en statistieken.

## Starten

De applicatie gebruikt SQLite. Je hoeft dus geen XAMPP, MySQL/MariaDB of
phpMyAdmin te starten.

Maak het lokale databasebestand en de tabellen aan met:

```powershell
python setup_database.py
```

Wil je de database leeg opnieuw aanmaken:

```powershell
python setup_database.py --fresh
```

Installeer daarna de dependencies:

```powershell
python -m pip install -r requirements.txt
```

Start het spel:

```powershell
python main.py
```

## Startmenu

- Typ je nickname.
- `F` of de knop rechtsboven: wissel fullscreen/venster.
- Pijltjes links/rechts: kies bordgrootte tussen 8x8 en 16x16. De standaard is 8x8.
- `N`: start een nieuw spel en plaats daarna handmatig je vloot.
- Pijltjes omhoog/omlaag: selecteer een opgeslagen spel.
- Enter of spatie: speel verder met het gekozen spel.
- `V`: bekijk de laatste opgeslagen staat van beide borden zonder meteen verder te spelen.
- `S`: wissel tussen opgeslagen spellen en statistieken.

## Vloot Plaatsen

- Klik op het eigen bord om het volgende schip te plaatsen.
- `R`: draai het schip horizontaal/verticaal.
- Backspace: haal het laatst geplaatste schip terug.
- Na het laatste schip worden asteroiden geplaatst en start het spel.

## Besturing Tijdens Het Spel

- Linkermuisknop op eigen bord: selecteer een schip.
- `A`: aanvalmodus, klik op het vijandelijke bord.
- `P`: speciale kracht, selecteer eerst een eigen schip en klik daarna op het juiste bord.
- `M`: bewegingsmodus, selecteer een eigen schip en gebruik de pijltjestoetsen.
- `O`: wissel de richting van de salvo-aanval.
- `C`: cheatcode aan/uit, toont het vijandelijke bord inclusief asteroidenrichting.
- `R`: herstart met dezelfde bordgrootte.
- `F` of `F11`: wissel fullscreen/venster.

Als het spel voorbij is, worden beide volledige opstellingen automatisch zichtbaar.

## Opslag En Statistieken

Spellen worden standaard opgeslagen in een lokale SQLite database:
`saves/cosmic_confrontation.sqlite3`. De database-instellingen staan in
`storage/config.py`; een database-server of `.env` is niet nodig.

Het statistiekenscherm toont per opgeslagen spel onder andere bordgrootte, aantal
beurten, geraakte vakjes en winnaar. De data staat in meerdere tabellen:

- `games`: basisgegevens per spel.
- `game_states`: volledige laatste spelstaat om verder te spelen.
- `game_actions`: losse actielog per beurt.
- `game_statistics`: hit/miss ratio, schepen over, gebruikte powerups, bewogen
  vakken en asteroideschade.
- `game_ships`: losse scheepsstatus per speler.
- `game_asteroids`: losse asteroideposities en richtingen.

## Opbouw

- `main.py`: startpunt.
- `presentation/ui.py`: Pygame-schermen, menu, plaatsingsscherm en rendering.
- `game.py`: spelstatus en beurtverloop.
- `storage/`: databaseconfiguratie, schema, opslag en statistiekberekening.
- `ai.py`: eenvoudige AI-beurt.
- `domain/board.py`: bordregels, schepen, aanvallen en asteroiden.
- `domain/ships/`: scheepstypes en speciale krachten.
- `domain/decorators.py`: eigen `audit_action` decorator voor actie-auditing.

## Technische Eisen

- Objectgeorienteerd: `GameBoard`, `Ship` en subklassen, `Asteroid`, `Player`,
  `AIPlayer` en `Move` zitten in aparte domeinmodules.
- `Ship` is een abstracte basisklasse voor de vijf scheepstypes.
- Dunder methods: naast initialisatie gebruikt `Ship` onder andere `__len__` en
  `__contains__`; `Player` gebruikt `__getattr__` om bordacties door te geven.
- Properties: `Ship.sunk`, `Ship.orientation` en `Game.selected_ship` schermen
  status en selectie af.
- List comprehensions staan onder andere in bordgeneratie, scans, vlootstatus en
  AI-keuzes.
- De eigen decorator `audit_action` wordt gebruikt op spel- en bordacties.
- `Move` valideert acties en maakt logregels voor aanval, beweging en speciale
  kracht.
- Opslag gebeurt in SQLite; iedere save bevat ook een statistiek-snapshot.
