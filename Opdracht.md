1
Eindopdracht - PYTHON
Avans Hogeschool, ’s-Hertogenbosch, studiejaar 2024/2025, versie 2.4
Reinout Versteeg, Jurgen Doreleijers
1 Wat is de opdracht?
"Cosmic Confrontation" is een digitaal tactiekspel waarbij spelers het bevel hebben
over een vloot ruimteschepen met als doel de vernietiging van een AI-bestuurde
vijandelijke vloot. Verderop worden de regels beschreven. De opdracht is om hier een
applicatie van te bouwen met Flask of PyGame.
2 Cosmic Confrontation
2.1 Spelregels en spelverloop
Cosmic Confrontation is een tactisch, turn-based bordspel waarin spelers (één
menselijke speler en één AI) commandanten zijn van rivaliserende vloten in de ruimte.
Het doel is om de vijandelijke vloot te vernietigen. Dit spel combineert strategische
plaatsing, slim gebruik van unieke schipvaardigheden, en voorspelling van
tegenstanders' bewegingen om te kunnen winnen.
Speelbord
Het spel wordt gespeeld op een vierkant bord, variërend van 8x8 vakjes tot 16x16
vakjes. Er zijn in totaal vijf verschillende soorten schepen. De grootte van het bord
wordt gekozen door de menselijke speler. Ook drijven er asteroïde rond op het
speelbord.
Vlootopstelling
Aan het begin van het spel positioneren beide spelers hun schepen op het bord.
Schepen mogen horizontaal of verticaal geplaatst worden en mogen niet overlappen
of de randen van het bord overschrijden. Ze mogen wel tegen elkaar aan staan.
Soorten schepen en hun krachten
1. Verkenner (lengte: 2, aantal: 2)
Speciale kracht: "Radar Scan" - Eenmalig gebruik (per spel) om een specifiek 3x3
gebied te scannen. Toont direct of er schepen op de specifieke vakjes staan, zonder ze
te beschadigen.
2. Jager (lengte: 3, aantal: 2)
2
Speciale kracht: "Homing Missile" - Eenmalig gebruik om de aanval altijd een
vijandelijk schip te laten raken. Zoekt het dichtstbijzijnde schip ten opzichte van de
gekozen positie op het bord.
3. Kruiser (lengte: 3, aantal 2)
Speciale kracht: "EMP Uitschakeling" - Kan eenmaal worden gebruikt om een
vijandelijk schip te deactiveren, waardoor de speciale kracht van dat schip niet meer
te gebruiken is en het schip niet te verplaatsen is voor drie beurten. Hiervoor moet
een (deel van het) schip zichtbaar zijn en geselecteerd worden door de speler.
4. Slagschip (lengte: 4, aantal: 1)
Speciale kracht: "Salvo Aanval" - Eenmalig gebruik om een aanval te doen die drie
aangrenzende vakjes tegelijkertijd raakt (horizontaal of verticaal), ideaal voor het snel
uitschakelen van langere schepen.
5. Commandoschip (lengte: 5, aantal 1)
Speciale kracht: "Space Smoke" - Eenmalig te gebruiken om een 3x3 gebied weer
(opnieuw) onzichtbaar te maken voor de tegenstander, tot er weer op geschoten
wordt.
Asteroïde
Nadat de vlootopstelling gemaakt is, worden er vier asteroïde op random plaatsen
gezet, waar nog geen schip staat én minimaal op één vak afstand van een schip, op het
speelbord. Elke asteroïde wordt geïnitialiseerd met een willekeurige diagonale
beweegrichting en kan aan het einde van de beurten één diagonaal vakje verplaatsen.
Spelverloop
Beide borden worden getoond aan de menselijke speler: het bord waar de schepen
van de AI op staan en het bord waar de eigen schepen op geplaatst zijn. Alle vakjes
zijn in het begin “onbekend”, dat wil zeggen dat je niet weet wat er op dat vakje staat.
Het spel wordt gespeeld in rondes, waarbij spelers om beurten één van de volgende
acties uitvoeren:
1. Aanval: specificeer een grid-coördinaat om aan te vallen. Als een vijandig
schip in het aangevallen vakje ligt, dan wordt dat schip geraakt. Is het schip
geraakt op alle plekken, dan verdwijnt deze in een zwart gat. Na de aanval
blijft het vakje “exposed”. Toon dit aan door middel van een achtergrond-
kleur, randkleur of een andere duidelijke visuele aanwijzing. Wordt een
asteroïde geraakt, dan veranderd de bewegingsrichting van de asteroïde naar
een andere diagonaal.
2. Beweging: verplaatst een schip één vakje in de lengterichting (mag beide
kanten op), mits het nieuwe vakje niet geblokkeerd wordt door andere
schepen of het einde van het bord. Komt het schip tegen een asteroïde aan,
dan krijgt het schip schade op die plaats en verdwijnt de asteroïde.
