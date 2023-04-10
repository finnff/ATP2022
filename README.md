# finnff ATP Bezem 22/23
## Project- en Testplan
Schrijf een project en testplan voor jouw geselecteerde casus (dit mag ook je INNO project zijn als dit voldoet aan de minimale eisen voor een project). Gebruik voor het schrijven van een project en testplan bijvoorbeeld deze https://www.guru99.com/what-everybody-ought-to-know-about-test-planing.html template.

Het project moet voldoen aan de volgende minimale eisen:

- Je gaat een regelsysteem bouwen (prototype) voor een systeem dat tenminste twee regelwaardes heeft (bijv. temperatuur en volume), die met elkaar in verband gebracht dienen te worden. Denk bijvoorbeeld aan een controlesysteem voor het regelen van het chloorgehalte en de temperatuur van het zwemwater in een zwembad, of de kleur en hoeveelheid van een drankje in een drankjesmixer, of een cruisecontrol voor je skateboard (die kan accelereren én afremmen).
- Je systeem bevat tenminste twee sensoren (om de toestand van het systeem te kunnen meten) en tenminste twee actuatoren (om de toestand van het systeem te kunnen beinvloeden).
- Het controlesysteem is geïmplementeerd volgens het Functional Reactive Programming principe (d.w.z. dat de aansturingsfuncties alleen puur functioneel dienen te zijn!).
- De realisatie van dit controlesysteem zal worden gedaan in Python, maar tenminste één component (sensor, actuator) wordt aangestuurd door een (bestaande) C++-bibliotheek (bijv. uit HWLib, of van Arduino). Hiervoor zal je een passende C++-Python koppeling moeten realiseren.
- Je project wordt individueel uitgevoerd, d.w.z. dat jij alleen verantwoordelijk bent voor de oplevering en inlevering van jouw project!

Let op: je hoeft het systeem niet daadwerkelijk te bouwen, alleen het ontwerpen en testen van de software is voldoende! Het is een expliciet onderdeel van de opgave dat je de hardware en de koppeling met de hardware via software mockt/simuleert. Tevens bied dit je de mogelijkheid om iets voor te stellen met dure of op korte termijn slecht te verkrijgen sensoren/actuatoren (bijv. een 3D-lidarLinks to an external site.), mits je de functionaliteit van de sensor/actuator via een datasheet of bestaande library kan achterhalen!

Je project- en testplan dient tenminste het volgende te bevatten:

- Een heldere beschrijving van de door jouw geselecteerde casus; wat voor controlesysteem ga je maken, waar dient het voor, welke waardes zijn er belangrijk, welke (soort) sensoren wil je gaan gebruiken, etc.
- Een architectuurschets van je op te leveren systeem, eentje voor de hardware (welke componenten ga je gebruiken, hoe zijn die verbonden) én eentje voor de software (welke classes/entiteiten wil je onderscheiden, welke interfaces zitten daartussen, etc.).
- Een heldere en gemotiveerde selectie van testen die je uit wilt voeren op het systeem waarbij (leg uit waarom deze component moet worden getest, en waarom deze test dat bereikt!):
    - Tenminste één element wordt getest door middel van één of meerdere unit tests;
    - Tenminste één interface wordt getest door middel van één of meerdere integratietests;
    - Tenminste één kenmerk van het systeem (kwaliteitscriterium) wordt getest door middel van één of meerdere systeemtests.

- Voor een voldoende dien je tenminste één unit, één integratie en één systeemtest te realiseren,  verdere test-realisaties kunnen leiden tot bonuspunten. 

Het project- en testplan is nodig om een GO te krijgen op het realiseren van de eindopdracht, maar telt tevens voor 30% van je cijfer voor Advanced Technical Programming en daarmee 15% van je cijfer voor het onderdeel kennisroutes van dit innovation semester (INNO). 

Lever je project- en testplan in als document (Word of pdf), of submit een git-link naar een repo waar je ze bewaard.


## Eindopdracht
Doorloop het ontwikkeltraject voor het maken van het prototype van de controlesoftware voor jouw systeem. Deze opdracht is individueel.

Denk aan de noodzakelijke onderdelen voor het project (zie ook Project- en testplan):

- Maak een regelsysteem dat tenminste twee sensoren en twee actuatoren gebruikt;
- Het regelsysteem dient geprogrammeerd te zijn volgens het Functional Reactive Programming principe (d.w.z. alle aansturingsfuncties zijn puur functioneel), met uitzondering van de loop die nodig is om tijd/state van het systeem bij te houden;
- Er is gebruik gemaakt van tenminste één Aspect-Oriented geprogrammeerde decorator (bijv. om de timing van functies te meten of logging toe te voegen);
- Er is gebruik gemaakt van tenminste één Python-C++ binding om een sensor/actuator aan te sturen door een (bestaande) C++-bibliotheek (zie https://realpython.com/python-bindings-overview/Links voor informatie over het maken van zulke bindings).

Daarnaast dien je uiteraard je systeem te testen volgens de door jouw voorgestelde tests in het project- en testplan, herinner je de daarvoor geldende minimale eisen:

- Voor een voldoende is er tenminste één unit test, één integratietest en één systeemtest gerealiseerd, verdere test-realisaties kunnen leiden tot bonuspunten;

Het maken van een volledige simulator om de onderdelen te testen is niet noodzakelijk, maar wordt wel gewaardeerd met bonuspunten.
In te leveren:
- Code van de diverse onderdelen (mag via een Git-link);
- (Korte) rapportage van de tests die uitgevoerd zijn om de kwaliteit van de software te garanderen.