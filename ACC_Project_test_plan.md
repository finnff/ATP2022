#

# Project en Testplan *Adaptive Cruise Control*

## Finn Fonteijn ATP Bezem 22/33

### Hardware Used

    Sensors:
    * Front Facing Radar
    * Speedometer (Wheel speed Sensor)
<https://www.bosch-mobility.com/en/solutions/sensors/front-radar-sensor/>

<https://www.bosch-mobility.com/media/global/products-and-services/passenger-cars-and-light-commercial-vehicles/driver-assistance-systems/multi-camera-system/front-radar-plus/onepager_front-radar_en_200608.pdf>

Infineon TLE5041plusC
<https://nl.mouser.com/ProductDetail/Infineon-Technologies/TLE5041PLUSCAAMA1?qs=3Bi3m9r5MQasB7gUvrCn8A%3D%3D>

<https://www.infineon.com/dgdl/Infineon-TLE5041PLUSC-DataSheet-v01_02-EN.pdf?fileId=5546d46265f064ff016632437f574f75o>

# CASUS_A

Projecttitel: Adaptive Cruise Control Systeem (ACCS)

Casusbeschrijving:
Het doel van dit project is het ontwikkelen van een adaptief cruise control systeem (ACCS) voor een voertuig. Het systeem regelt de snelheid van het voertuig en de afstand tot het voorliggende voertuig, waarbij gebruik wordt gemaakt van de volgende sensoren en actuatoren:
Sensoren:

Wheel speed sensor: meet de snelheid van de wielen
Front facing radar sensor: meet de afstand tot het voorliggende voertuig
Actuatoren:

Gaspedaal: regelt de acceleratie van het voertuig
Remsysteem: regelt het afremmen van het voertuig
Architectuurschetsen:
Hardware:
De wheel speed sensor is verbonden met de wielen van het voertuig en stuurt de snelheidsinformatie naar de centrale verwerkingsunit (CPU). De front facing radar sensor is aan de voorzijde van het voertuig geplaatst en stuurt afstandsgegevens naar de CPU. De CPU stuurt de signalen naar de actuatoren (gaspedaal en remsysteem).
Software:
De software bestaat uit verschillende klassen die de sensoren, actuatoren, CPU en algoritmes voor ACCS bevatten. De interfaces tussen de klassen zijn gedefinieerd om gegevens uit te wisselen en de algehele werking van het systeem te coördineren.

Testplan:
Het testplan omvat unit tests, integratietests en systeemtests om de betrouwbaarheid en functionaliteit van het ACCS te garanderen.
Unit tests:

Test de nauwkeurigheid van de wheel speed sensor en de front facing radar sensor om te verzekeren dat zij correcte gegevens aanleveren.
Test de functionaliteit van het gaspedaal en het remsysteem om te controleren of ze correct reageren op de input van de CPU.
Integratietests:

Test de communicatie tussen de sensoren en de CPU, en tussen de CPU en de actuatoren, om te waarborgen dat gegevens correct worden uitgewisseld en het systeem op de juiste manier reageert op sensorinput.
Systeemtests:

Test het adaptieve cruise control algoritme onder verschillende verkeersomstandigheden en snelheden om te controleren of het systeem correct functioneert en veilig en comfortabel rijgedrag bevordert.
De uitvoering van deze tests zorgt voor een grondige evaluatie van het ACCS, waarbij de betrouwbaarheid en prestaties van het systeem worden beoordeeld.

# CASUS_B

Project- en Testplan Adaptive Cruise Control

Beschrijving van de casus
Het doel van dit project is om een prototype van een adaptive cruise control systeem te ontwerpen en te testen. Dit systeem moet in staat zijn om automatisch de snelheid van een voertuig aan te passen aan de snelheid van het voorliggende voertuig. Het systeem maakt gebruik van een front-facing radar sensor en een wheel speed sensor om de afstand en snelheid tot het voorliggende voertuig te meten. Op basis van deze metingen stuurt het systeem de actuatoren gas geven en afremmen aan om de snelheid van het voertuig te regelen. Het doel is om een veilig en comfortabel rijgedrag te realiseren, waarbij de bestuurder zich kan concentreren op andere taken, zoals het sturen.

Architectuurschets
Het systeem bestaat uit verschillende componenten:

Front-facing radar sensor: meet de afstand en snelheid tot het voorliggende voertuig
Wheel speed sensor: meet de snelheid van het voertuig
Regelsysteem: verwerkt de meetwaarden van de sensoren en stuurt de actuatoren aan om de snelheid van het voertuig te regelen
Gas geven en afremmen actuatoren: passen de snelheid van het voertuig aan op basis van de aansturing van het regelsysteem
Het regelsysteem is geïmplementeerd volgens het Functional Reactive Programming principe. Het systeem is geschreven in Python en maakt gebruik van de C++-bibliotheek van de front-facing radar sensor.

Testen
Om het systeem te testen, worden verschillende soorten testen uitgevoerd:

Unit test:
Het regelsysteem wordt getest met behulp van een unit test. Deze test controleert of het regelsysteem de meetwaarden van de sensoren op de juiste manier verwerkt en de actuatoren op de juiste manier aanstuurt. De test maakt gebruik van simulatiedata voor de sensoren en actuatoren.

Integratietest:
De interface tussen het regelsysteem en de front-facing radar sensor wordt getest met behulp van een integratietest. Deze test controleert of de communicatie tussen het regelsysteem en de sensor correct verloopt. De test maakt gebruik van simulatiedata voor de sensor.

Systeemtest:
Het rijgedrag van het voertuig wordt getest met behulp van een systeemtest. Deze test controleert of het systeem in staat is om een veilig en comfortabel rijgedrag te realiseren. De test maakt gebruik van simulatiedata voor de sensoren en actuatoren, en wordt uitgevoerd in een simulatie-omgeving waarin verschillende scenario's worden nagebootst, zoals een voertuig dat plotseling remt of van rijbaan verandert.

Conclusie
Met behulp van de verschillende testen kan worden gecontroleerd of het adaptive cruise control systeem voldoet aan de gestelde eisen. Door simulatiedata te gebruiken kan het systeem worden getest zonder daadwerkelijk een voertuig te gebruiken, wat kosten en risico's verlaagd.


---------

Projecttitel: Adaptief Cruise Control Systeem (ACCS)

Casusbeschrijving:
Het doel van dit project is het ontwikkelen en testen van een adaptief cruise control systeem (ACCS) voor een voertuig. Het systeem regelt de snelheid van het voertuig en de afstand tot het voorliggende voertuig, waarbij gebruik wordt gemaakt van de volgende sensoren en actuatoren:

Sensoren:

Wheel speed sensor: meet de snelheid van de wielen
Front facing radar sensor: meet de afstand tot het voorliggende voertuig
Actuatoren:

Gaspedaal: regelt de acceleratie van het voertuig
Remsysteem: regelt het afremmen van het voertuig
Architectuurschets:
Hardware:
De wheel speed sensor is verbonden met de wielen van het voertuig en stuurt de snelheidsinformatie naar de centrale verwerkingsunit (CPU). De front facing radar sensor is aan de voorzijde van het voertuig geplaatst en stuurt afstandsgegevens naar de CPU. De CPU stuurt de signalen naar de actuatoren (gaspedaal en remsysteem).

Software:
Het regelsysteem is geïmplementeerd volgens het Functional Reactive Programming principe en bestaat uit verschillende klassen die de sensoren, actuatoren, CPU en algoritmes voor ACCS bevatten. De interfaces tussen de klassen zijn gedefinieerd om gegevens uit te wisselen en de algehele werking van het systeem te coördineren. Het systeem is geschreven in Python en maakt gebruik van de C++-bibliotheek van de front-facing radar sensor.

Testplan:
Het testplan omvat unit tests, integratietests en systeemtests om de betrouwbaarheid en functionaliteit van het ACCS te garanderen.

Unit tests:

Test de nauwkeurigheid van de wheel speed sensor en de front facing radar sensor om te verzekeren dat zij correcte gegevens aanleveren.
Test de functionaliteit van het gaspedaal en het remsysteem om te controleren of ze correct reageren op de input van de CPU.
Integratietests:

Test de communicatie tussen de sensoren en de CPU, en tussen de CPU en de actuatoren, om te waarborgen dat gegevens correct worden uitgewisseld en het systeem op de juiste manier reageert op sensorinput.
Test de interface tussen het regelsysteem en de front-facing radar sensor om te controleren of de communicatie tussen het regelsysteem en de sensor correct verloopt.
Systeemtests:

Test het adaptieve cruise control algoritme onder verschillende verkeersomstandigheden en snelheden om te controleren of het systeem correct functioneert en veilig en comfortabel rijgedrag bevordert.
Test het rijgedrag van het voertuig met behulp van een simulatie-omgeving waarin verschillende scenario's worden nagebootst, zoals een voertuig dat plotseling remt of van rijbaan verandert.
Conclusie:
Met behulp van de verschillende testen kan worden gecontroleerd of het adaptive cruise control systeem voldoet aan de gestelde eisen. Door simulatiedata te gebruiken kan het systeem worden getest zonder daadwerkelijk een voertuig te gebruiken, wat kosten en risico's verlaagd.



#  Adaptive Cruise Control Systeem (ACCS) IEEE 829 Testplan
(Op basis van <https://www.mammoth-ai.com/how-to-write-a-test-plan-with-the-ieee-829-standard/>)

1. Test plan identifier:
    ACCS Testplan v1.0

2. Introduction:
Dit testplan beschrijft de testprocedures en teststrategie voor het Adaptive Cruise Control Systeem (ACCS), dat de snelheid en afstand tot het voorliggende voertuig regelt met behulp van wheel speed sensors, front facing radar sensors, gaspedaal en remsysteem.

3. Test items:
De test items omvatten de volgende componenten van het ACCS:

- Wheel speed sensor
- Front facing radar sensor
- Gaspedaal
- Remsysteem
- CPU
- ACCS algoritme

4. Features to be tested:
De te testen functies zijn:

- Nauwkeurigheid van de wheel speed sensor en front facing radar sensor
- Functionaliteit van het gaspedaal en het remsysteem
- Communicatie tussen sensoren, CPU en actuatoren
- Adaptieve cruise control algoritme onder verschillende verkeersomstandigheden en snelheden

5. Features not to be tested:

- Niet-ACCS gerelateerde voertuigsystemen
- Interactie tussen ACCS en bestuurder
- Hardware- en software compatibiliteit met andere voertuigsystemen

6. Item pass/fail criteria:
De volgende criteria worden gebruikt om te bepalen of een testitem slaagt of faalt:

- Nauwkeurigheid van sensoren binnen specificaties
- Correcte werking van actuatoren volgens input van de CPU
- Ononderbroken en foutloze communicatie tussen componenten
- Veilig en comfortabel rijgedrag onder verschillende verkeersomstandigheden

7. Suspension criteria and resumption requirements:
Testen worden opgeschort als een van de volgende situaties zich voordoet:

- Kritieke hardware- of softwarefouten
- Onveilige testomstandigheden
- Onvoldoende testresultaten
Hervatting van de tests zal plaatsvinden zodra de problemen zijn opgelost en de testomgeving weer veilig en functioneel is.

8. Test deliverables:
De volgende test deliverables zullen worden opgeleverd:

- Testplan
- Test cases en testscripts
- Test dataverzameling en analyse
- Testrapport

9. Testing tasks:
De tests zullen de volgende taken omvatten:

- Voorbereiding van testomgeving en test cases
- Uitvoeren van unit tests, integratietests en systeemtests
- Analyseren van testresultaten
- Opstellen van testrapport

10. Environmental needs:
De testomgeving omvat een gesimuleerd of echt voertuig met de ACCS-componenten geïnstalleerd en operationeel. Een testtraject zal worden voorbereid voor systeemtests, met verschillende verkeersomstandigheden en snelheden om de prestaties van het ACCS te evalueren.

11. Responsibilities:
Het testteam is verantwoordelijk voor het plannen, uitvoeren en analyseren van de tests en het opstellen van het testrapport. Het ontwikkelteam is verantwoordelijk voor het oplossen van eventuele problemen die tijdens de tests worden geïdentificeerd.

12. Staffing and training needs:
Het testteam zal bestaan uit ervaren test engineers met kennis van voertuigsystemen, sensoren en actuatoren. Indien nodig, zal aanvullende training worden verzorgd om het team vertrouwd te maken met de specifieke aspecten van het ACCS en de gebruikte testapparatuur.

14. Schedule:
De tests zullen volgens het volgende schema worden uitgevoerd:

- Week 1: Voorbereiding van testomgeving en test cases
- Week 2-3: Unit tests en integratietests
- Week 4-5: Systeemtests
- Week 6: Analyse van testresultaten en opstellen van testrapport

15. Risks and contingencies:
Mogelijke testrisico's zijn onder meer:

- Onnauwkeurige of onbetrouwbare sensoren en actuatoren
- Fouten in de communicatie tussen componenten
- Beperkingen in de testomgeving of testapparatuur

In geval van problemen zullen er geschikte maatregelen worden genomen om de impact op het testschema te minimaliseren en de kwaliteit van de testresultaten te waarborgen.
16. Approvals:
Het testplan zal ter goedkeuring worden voorgelegd aan de projectmanager, de verantwoordelijke voor het ontwikkelteam en eventuele andere belanghebbenden. Na goedkeuring van het testplan zullen de tests worden uitgevoerd volgens het opgestelde schema.
