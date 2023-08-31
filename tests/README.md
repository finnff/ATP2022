# TestRapport


# Unit Test 1  Measures Speed calculator  (./src/WheelSpeedCPP/wsp_mod.so) bestaande uit  (./src/WheelSpeedCPP/aaaa/aaaa.cpp)




## Unit Test: MeasuredSpeedCalculator

### Motivatie
De MeasuredSpeedCalculator is een cruciaal onderdeel van het systeem, aangezien het de snelheid van het voertuig probeert
te berekenen op basis van de input van de WheelSpeedSensor. 
 Een nauwkeurige snelheidsberekening is essentieel voor het ACC systeem, waardoor het op een veilige afstand tot het voorliggende voertuig kan blijven. 
  Als de MeasuredSpeedCalculator onjuiste snelheden berekent, heeft dit via de CPU invloed op het op het GasPedaal en Remsysteem. Fouten of ongewenst gedrag in deze 2 actuatoren
   kan dit leiden tot onveilige situaties en mogelijk ongevallen. Het testen van deze component is daarom noodzakelijk
   om te waarborgen dat het systeem goed functioneert en om de veiligheid te garanderen.

     
### Testprocedure 

Testen of de MeasuredSpeedCalculator de snelheid van het voertuig correct berekent op basis van verschillende inputwaarden(Hatchback,SUV,Ferrari) van de WheelSpeedSensor, Wieldiameter en CPR van het encoderwiel.

1. Bereid testscenario's voor met verschillende inputwaarden voor de WheelSpeedSensor, Wieldiameter en CPR van het encoderwiel. Gebruik realistische waarden die overeenkomen met verschillende voertuigtypen (bijv. Hatchback, SUV, Ferrari).
2. Voer de testscenario's uit met behulp van de Simulator, en leg zowel de berekende snelheden, als de TrueVehicleSpeed uit de Simulator vast.
3. Vergelijk de berekende snelheden met de TrueVehicleSpeed, rekening houdend met de variabelen van de verschillende soorten autos uit de testscenario's. 
4. Controleer of de berekende snelheden binnen een acceptabele foutmarge(+- 2.0%) van de verwachte snelheden vallen. Als dit niet het geval is, onderzoek dan de oorzaak en pas de implementatie van de MeasuredSpeedCalculator (of WheelSpeedSensor) aan indien nodig.
5. Herhaal de testprocedure totdat de berekende snelheden consistent nauwkeurig(i.e. binnen de foutmarge) zijn voor alle testscenario's.


Deze testprocedure is ontworpen met verschillende belangrijke aspecten in gedachten om de nauwkeurigheid van de snelheidsberekeningen te waarborgen en de veiligheid van het systeem te garanderen:

- Realistische waarden worden gebruikt voor de inputvariabelen om de prestaties van het systeem in de praktijk te beoordelen.
- Het vastleggen van zowel de berekende snelheden als de TrueVehicleSpeed stelt ons in staat om objectief de nauwkeurigheid van de berekeningen te beoordelen.
- Door een kleine foutmarge te gebruiken, wordt rekening gehouden met de beperkingen van floating-point precisie en kleine nauwkeurigheidsfouten in de sensors.
- Het herhalen van de testprocedure zorgt voor betrouwbaarheid en verkleint de kans op onveilige situaties of ongevallen.

Door deze testprocedure te volgen, kunnen we de nauwkeurigheid van de snelheidsberekening garanderen en voorkomen dat ongewenst gedrag van het GasPedaal en Remsysteem leidt tot onveilige situaties en mogelijk ongevallen.



HIER ONDER LEZEN
HIER ONDER LEZEN
HIER ONDER LEZEN
HIER ONDER LEZEN
HIER ONDER LEZEN



De Measuresed Speed snso werkt voor alle sorten wielen, ook bij bewegeing , hoewel in eerste we de foutmarge wel haal maar dat er nog wel relatief veel foutmarge zit in het lezenv van de sensor:

##########


```json
{
    "Param Name": "Ferrari F69",
    "Wheel Diameter": 0.71,
    "Encoder CPR": 40,
    "Param Name": "Golf GTI/GTE",
    "Wheel Diameter": 0.625,
    "Encoder CPR": 45,
    "Param Name": "BMW X27",
    "Wheel Diameter": 0.838,
    "Encoder CPR": 60,
}
```

De Measured Speed sensor is ontworpen om compatibel te zijn met verschillende soorten wielen en bewegingsomstandigheden. Uit de eerste testresultaten blijkt dat we binnen de gespecificeerde foutmarge van ±2.0% vallen. Hier zijn enkele voorbeeldresultaten:

- True Speed: 12.03, Calculated Speed: 11.99, Delta: 0.04, Delta %: 0.30%
  
Hoewel we binnen de foutmarge zitten, is het belangrijk op te merken dat we een interne fout van 0.3% hebben gemodelleerd voor de sensor, zoals aangegeven op pagina 17 van de [Infineon-TLE5041PLUSC datasheet](https://www.infineon.com/dgdl/Infineon-TLE5041PLUSC-DataSheet-v01_02-EN.pdf?fileId=5546d46265f064ff016632437f574f75).

Hij is getest met de volgende 3 Autos:


```json
{
    "Param Name": "Ferrari F69",
    "Wheel Diameter": 0.71,
    "Encoder CPR": 40,

    "Param Name": "Golf GTI/GTE",
    "Wheel Diameter": 0.625,
    "Encoder CPR": 45,

    "Param Name": "BMW X27",
    "Wheel Diameter": 0.838,
    "Encoder CPR": 60,
}
```


De enige fouten die ik ben tegen gekomen gebeurden als ik handmatig (via de simulator) de snelheid van het voertuig ging veranderen, en dat de berekening van de oude snelheid al was gestart (Multi threaded concurreny ):

![img](img/2023-08-30-21-54-34.png)


```python
# Code voor het toevoegen van een willekeurige fout van ± 0.3% zoals gespecificeerd in de datasheet.
encoder_pulses_per_second *= 1 + random.choice([-0.003, 0.003])
````


Wanneer deze sensorfout wordt verwijderd uit de simulatie, zijn de foutmarges extreem laag, wat betekend dat onze code en C++-binding zeer nauwkeurig zijn in het berekenen van de snelheid, ongeacht het voertuigtype en de wielgrootte.

```
True Speed: 12.300423,          Calculated Speed: 12.30042076110839, Delta: 2.2388916018911686e-06, Delta %: 1.820174478464008e-05, Elapsed Time: 0.00011110305786132812, 1/Elapsed Time: 9000.652360515021
True Speed: 12.410620000000002, Calculated Speed: 12.41061782836914, Delta: 2.1716308609143198e-06, Delta %: 1.749816577184959e-05, Elapsed Time: 0.0001347064971923828,  1/Elapsed Time: 7423.546902654867
True Speed: 12.519560000000002, Calculated Speed: 12.51955795288086, Delta: 2.047119142645215e-06,  Delta %: 1.63513665228268e-05,  Elapsed Time: 0.0001900196075439453,  1/Elapsed Time: 5262.614805520702
```
Dit suggereert dat het merendeel van de geobserveerde fout waarschijnlijk toe te schrijven is aan de sensor zelf en niet aan mijn implementatie van WheelSpeedSensor. Het enige andere type fout dat aanwezig is, betreft minimale verschillen veroorzaakt door het omzetten van floating-point getallen naar Integers. 





## Integratietest: WheelSpeedSensor's industriele 12V Current Modulation interface

### Motivatie

*De communicatie tussen de WheelSpeedSensor en de MeasuredSpeedCalculator is noodzakelijk voor het berekenen van de snelheidsberekeningen.*
*Als deze interface niet goed werkt, levert dit misschien onjuiste data voor de MeasuredSpeedCalculator. Dit zal problemen opleveren voor de hierboven genoemde Unit Test.*
*Het testen van de interface helpt om te waarborgen dat het systeem correct functioneert en draagt bij aan de veiligheid.*
*Test: Testen of de 12V Current Modulation-interface de High/Low current outputs van de WheelSpeedSensor correct doorstuurt naar de MeasuredSpeedCalculator en of de MeasuredSpeedCalculator deze signalen correct interpreteert om de snelheid van het voertuig te berekenen.*

*### Testprocedure*

*- Zorg ervoor dat de WheelSpeedSensor en de MeasuredSpeedCalculator correct zijn aangesloten via de 12V Current Modulation-interface. (In ons geval is dit de C++/Python Bindings en de communicatie hiertussen)*
*- Simuleer verschillende rotatiesnelheden van het wiel, met de WheelSpeedSensor daarop aangesloten.*
*- Monitor de High/Low current outputs die door de WheelSpeedSensor worden gegenereerd op basis van de rotatiesnelheid van het wiel en verifieer of deze correct worden doorgegeven via de 12V Current Modulation-interface.*
*- Controleer of de MeasuredSpeedCalculator de ontvangen High/Low current outputs correct interpreteert en of de berekende snelheid overeenkomt met de werkelijke snelheid van het wiel (rekening houdend met de wieldiameter en de CPR van het encoderwiel).*
*- Voer deze test uit voor verschillende rotatiesnelheden van het wiel om te verifiëren of de interface en de MeasuredSpeedCalculator onder verschillende omstandigheden correct functioneert.*

*De testprocedure controleert of de 12V Current Modulation-interface correct werkt en of de MeasuredSpeedCalculator de signalen nauwkeurig interpreteert. Hierdoor wordt de nauwkeurige snelheidsberekening gegarandeerd en de veiligheid van het systeem gewaarborgd. Het testen van verschillende rotatiesnelheden zorgt ervoor dat het systeem onder uiteenlopende omstandigheden correct functioneert.*


HIER ONDER LEZEN
HIER ONDER LEZEN
HIER ONDER LEZEN
HIER ONDER LEZEN
HIER ONDER LEZEN




Test gefaald:
Dat de unit test hierboven zo goed werkt is niet voor niets. Oorspronkelijk heb ik geprobeerd om, zoals ooit bedacht in het projecttestplan, het hardwaredeel 'WheelSpeedSensor' (de ADC-achtige Infineon-TLE5041PLUSC) en het softwaredeel `MeasuredSpeedCalculator` apart te houden. Waar de ene enkel waarden las, had de andere informatie over de auto Wielgrote om deze terug te rekenen naar echte snelheid. Zoals hierboven beschreven, heb ik eerst (via Python sockets zelfs nog) geprobeerd om met HI-LO signalen te versturen vanuit de TrueVehicleSpeed, die dan vervolgens opgevangen zouden moeten worden door een ander stuk Python-code. Dit werkte absoluut niet goed. Ik heb was aan het proberen om een soort binaire digital-to-analog-converter te maken die de timinginformatie van data over de Python-implementatie van de sockets netwerkinterface? beheerde. Issues hier mee was een belangrijke reden om over te schakelen naar Redis voor betere prestaties. Hoewel dit hielp en we (na filtering en averaging) wel een getal hadden dat gerelateerd was aan de snelheid, varieerde dit enorm (+- 50%) en was het dus niet geschikt voor gebruik. Dit lijkt meer een implementatiefout te zijn dan slecht ontwerp, aangezien ik met een echte TLE5041 hardware sensor eigenlijk geforceerd was om het zo te maken.


Hierdoor heb ik ervoor gekozen om de twee componenten samen te voegen in één bestand. In plaats van HI-LO signalen slaan we nu de 'WheelSpeedSensorHz' op en versturen we deze als interproces-item. Door deze abstractie toe te passen, moeten we nog steeds rekening houden met de diameter en de encoderwiel-count. Dit komt omdat we eerst in de simulator met de werkelijke data deze waarden moeten omrekenen naar het aantal pulsen dat deze sensor zou uitzenden, gebaseerd op de gegeven autospecificaties.


Het resultaat is dat de code hiervoor werd samengevoegd, deze is later nog omgeschreven naar C++ voor de binding. We sturen ook data (CPR en diameter) naar deze C++-binding, zodat we de hele berekening hierin kunnen uitvoeren.

```cpp
float WheelSpeedSensor::read_speed(){
    redisReply* reply = (redisReply*)redisCommand(redis_client, "HGET Sensor_Actuator WheelSpeedSensorHz");
    float encoder_pulses_per_second = 0.0;
    if (reply->type == REDIS_REPLY_STRING) {
        encoder_pulses_per_second = std::atof(reply->str);
    }
    freeReplyObject(reply);
    // Convert pulses per second naar rotations
    float rotations_per_second = encoder_pulses_per_second / this->cpr;

    // Calculate the wheel circumference we use this instead of math.h pi good enough
    float wheel_circumference = 3.141592 * this->diameter;

    // Convert to speed in meters per second
    float true_vehicle_speed = rotations_per_second * wheel_circumference;

    return true_vehicle_speed;
}
void WheelSpeedSensor::set_cpr(float cpr){
    this->cpr = cpr;
}
void WheelSpeedSensor::set_diameter(float diameter){
    this->diameter = diameter;
}
```


Zoals te zien is in de loguitvoer en in `/UnitTest/removedInternalError.log`, is het zelfs met C++ niet echt snel (varieerde tussen 5000-9000 Hz voor alleen de read_speed()-operatie). Dit zou waarschijnlijk ook onvoldoende zijn geweest als ik het op mijn oorspronkelijke manier had gemaakt, waarschijnlijk niet via Redis, omdat deze te langzaam is.


```
True Speed: 12.300423,          Calculated Speed: 12.30042076110839,  Elapsed Time: 0.00011110305786132812, 1/Elapsed Time: 9000.652360515021
True Speed: 12.410620000000002, Calculated Speed: 12.41061782836914,  Elapsed Time: 0.0001347064971923828,  1/Elapsed Time: 7423.546902654867
True Speed: 12.519560000000002, Calculated Speed: 12.51955795288086,  Elapsed Time: 0.0001900196075439453,  1/Elapsed Time: 5262.614805520702
```






## Systeemtest: ACCS houdt Veilige afstand in verschillende verkeersscenario's

### Motivatie

Het belangrijkste doel (kwaliteitscriterium) van het ACCS is het behouden van een veilige afstand tot het voorliggende voertuig. Het testen van het systeem in verschillende verkeerssituaties en snelheden helpt om te waarborgen dat het systeem correct functioneert, betrouwbaar en veilig is, en voldoet aan de gestelde kwaliteitseisen.*

### Testprocedure

1. Bereid verschillende verkeerssituaties en snelheden voor, die het ACCS-systeem zou kunnen tegenkomen in real-world scenario's (bijv. stadsverkeer, snelwegverkeer, file, acceleratie en deceleratie, enz.). En implementeer deze scenario's in de Simulator.*
2. Voer de test in de simulator uit voor verschillende soorten auto's (Hatchback, SUV, Ferrari), voor elk van de voorbereide verkeersscenario's.
3. Monitor en registreer de volgende waarden tijdens elk scenario:
    - Afstand tot voorligger in meters*
    - MeasuredSpeed*
    - Afstand tot voorligger in seconden met de huidige MeasuredSpeed*
    - Het verschil tussen deze laatste waarde, en de constante 'gewenste afstand tot voorligger in seconden'*
4. Analyseer de resultaten om te bepalen of het ACCS-systeem de ingestelde veilige afstand tot het voorliggende voertuig in alle situaties heeft behouden.*
    - **Als de afstand tot de voorligger in meters 0 of negatief is, betekent dit dat er een botsing is geweest; dit is per definitie dus geen 'veilige afstand'***

We hebben een PID-systeem geïmplementeerd voor de controle van onze auto. Echter, het is zo slecht afgesteld dat het alleen effectief is voor willekeurige testgevallen in de Ferrari. De auto's reageren te verschillend om dezelfde set PID-waarden te gebruiken. Ik ben hieraan begonnen en heb zelfs een PyTorch-implementatie met een neuraal netwerk gebruikt, dat ongeveer 15 minuten nodig had om geschikte waarden te vinden. Desondanks is het me niet gelukt om het systeem veilig te laten werken voor alle drie de auto's. Omdat het wel is gelukt met de Ferrari, lijkt dit meer een kwestie van tijd dan een systeemfout.



HIER ONDER LEZEN
HIER ONDER LEZEN
HIER ONDER LEZEN
HIER ONDER LEZEN
HIER ONDER LEZEN

We hebben ook een simulator ontwikkeld die aangepaste testgevallen kan uitvoeren. De invoer hiervoor is een string-gebaseerde DSL (Domain Specific Language) die elk testgeval kan vertegenwoordigen. Elke actie in het testgeval kan een tuple zijn, weergegeven als een string.

Specification:
* pX: Pause for X seconds (e.g., p5 means pause for 5 seconds).
* mV=X: Set myVel to X (e.g., mV=30 means set true_vehicle_speed to 30).
* mAX=X: Set myAcc to X (e.g., mAX=1 means set true_vehicle_acceleration to 1).
* vV=X: Set voVel to X (e.g., vV=20 means set true_voorligger_speed to 20).
* d2v=X: Set dist2vo to X (e.g., d2v=100 means set true_distance_to_voorligger to 100).
* cc: Check if the vehicle has crashed and update the counters.
* R: Reset the simulation.
* +=X: Increment the last float value by X.
* -=X: Decrement the last float value by X.



Omdat ik niet echt gemakkelijk handmatig scenarios kon bedenken voor stadsverkeer, snelwegverkeer, file, etc, heb ik deze scenarios automatisch laten genereren als test cases.
zo is : ([9.46, 0.01, 14.24, 493.66], ['mV=5.41', 'p=4.61', 'mV=1.54', 'p=4.08', 'cc', 'R']) een valide test scenario die automatisch gegenereerd kan worden. Zie ./SysteemTest/random_test_cases.log voor een voorbeeld van deze testgevallen (en de code om deze te genereren).


