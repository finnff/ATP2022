#  Casusbeschrijving:
Het doel van dit project is het ontwikkelen van een adaptief cruise control systeem (ACCS) voor een voertuig. Het systeem regelt de snelheid van het voertuig en de afstand tot het voorliggende voertuig, waarbij gebruik wordt gemaakt van een Wheel speed sensor, Front Radar Sensor, Gas- en Rempedaal.

# Sensoren:
## MeasuredSpeedSensor
    Omdat de snelheid van een voortuig afhangt van hoe vaak die wielen roteren en hoe groot die wielen zijn, bestaat deze abstracte sensor uit twee losse 'sub-sensors' *WheelSpeedSensor* en een *MeasuredSpeedCalculator*

### **Wheel speed sensor**: meet de rotatiesnelheid van de wielen
#### Hardware: Infineon TLE5041plusC
De TLE5041plusC is een magnetische hoeksensor die de wielsnelheid kan meten dankzij het Hall-effect in combinatie met een roterende as of magneet. Deze sensor is speciaal ontwikkeld voor 'harsh automotive requirements' en heeft geen andere componenten nodig dan het magnetische encoderwiel dat vastgemaakt moet worden aan de as/wiel. 

De TLE5041plusC zet de sinusoïde(sterkte magnetischveld over tijd) die ontstaat als het wiel draait, om naar een High/Low signaal via een two-wire current interface. Deze sensor weet aleen iets over de rotatiesnelheid van het encoderwiel, niets over de snelheid van het voertuig.
De frequentie van deze veranderingen kan vervolgens door bv. een microcontroller (of onze C++/Python binding, zie MeasuredSpeedCalculator) samen met informatie over de grootte van het wiel en het aantal magneten op het encoderwiel (Counts Per Revolution = CPR) omgezet worden naar een snelheid in meters per seconde.

Kenmerken:

- Werkt van 1-5000hz (magnetisch veld veranderingen per seconde)
- Kosten 5.15 euro per stuk.
- Input voltage tussen 4.5v en 20v
- Interfaced over current modulation:
    +  Supply current - output low  :  7 mA
    +  Supply current - output high : 14 mA
- Self calibrating na 5 pulses


### MeasuredSpeedCalculator
#### C++ Code
Normaal zou dit door een apparte microcontroller, of de CPU zelf gedaan worden, maar we gaan dit als in C++ nabootsen. Hiervoor moeten we een current meter maken, zodat we het verschill in geleverde stroom van de wheelspeed sensor kunnen meten. Hieruit kunnen we de logic levels halen.
Naast dat de MeasuredSpeedCalculator C++ code de High/Low current outputs van de TLE5041plusC afleest rekent die ook met de frequentie/interval tussen deze outputs. Als dit bekent is kan de MeasuredSpeedCalculator samen met de gegeven constanten Wieldiameter en magnetic wheelencoder CPR de snelheid van het voertuig berekenen, *MeasuredSpeed*.




##  **Front facing radar sensor**: *meet de afstand tot het voorliggende voertuig in meters
De Bosch Front Radar is een radarsensor die de afstand tot het voorliggende voertuig meet. 
Deze sensor is speciaal ontwikkeld voor adaptieve cruise control systemen en biedt nauwkeurige en betrouwbare afstandsmetingen.
Hoewel de sensor over veel extra functies beschikt, zoals een breede field of view en fieter en voetgangersdetectie, is dit niet relevant voor het ACCS.
We zullen deze sensor als abstracte sensor zien die de afstand tot het voorliggende voertuig levert met de volgende kenmerken:

- Accuracy: 0,1 m
- Resolutie: 0,2 m
- Maximaal bereik: 210 m
- Update Rate: 500ms


# Actuatoren:

## Gaspedaal
Het Gaspedaal regelt de acceleratie van het voertuig (verhoogt TrueVehicleSpeed in de Simulator)
Met interface: 0-100% waar 100 versnellen is met de maximale acceleratie constante

## Remsysteem
Het Remsysteem regelt het afremmen van het voertuig (vermindert TrueVehicleSpeed in de Simulator)
Met interface: 0-100% waar 100 remmen is met de maximale deacceleratie constante

# Constanten:

- **Maximale acceleratieconstante in $m/s^2$:** een constante waarde die de maximale acceleratie van het voertuig vertegenwoordigt
- **Maximale vertragingconstante (remmen) in $m/s^2$:** een constante waarde die de maximale vertraging of vermindering van de snelheid van het voertuig vertegenwoordigt
- **Wieldiameter in meters:**  een maat die wordt gebruikt om de omtrek van het wiel (velg + band) te berekenen, wat nodig is om de snelheid van het voertuig te bepalen
- **Aantal counts per revolution van de wheelencoder voor wheel speed:**  een waarde die aangeeft hoeveel pulsen de wheelencoder genereert voor elke volledige omwenteling van het wiel; deze informatie wordt gebruikt om de snelheid van het voertuig te berekenen
- **Gewenste seconden afstand tot voorligger in S:** een constante waarde die aangeeft wat de minimale veilige tijd is die nodig is om een veilige afstand te behouden tussen het voertuig en de voorligger

De twee regelwaarden (**MeasuredSpeed** en **MeasuredAfstandTotVoorligger**) worden beïnvloed door de actuatoren (gaspedaal en remsysteem) op basis van de constanten die in het systeem zijn gedefinieerd. Door de maximale acceleratie- en vertragingconstanten kan het systeem de snelheid van het voertuig effectief realistisch(snelheid veranderen kost tijd) aanpassen om een veilige en comfortabele afstand tot het voorliggende voertuig te behouden. De informatie van de wheelencoder, in combinatie met de wieldiameter, stelt het systeem in staat om de MeasuredSpeed van het voertuig nauwkeurig te meten.

# Simulator 

Om het hele ACCS-systeem te simuleren, moeten we verschillende externe onderdelen implementeren die de werkelijke waarden en omstandigheden in het systeem vertegenwoordigen. Deze externe componenten zijn de "echte wereld" variabelen die moeten worden gemeten en gecontroleerd door het ACCS-systeem. Hier is een overzicht van de belangrijkste externe onderdelen die nodig zijn voor de simulatie:

- **TrueVehicleSpeed** : Dit is de werkelijke snelheid van het voertuig in de simulatie. Het ACCS-systeem moet deze waarde benaderen door middel van de VehicleSpeedCalculator en de WheelSpeedSensor.
- **TrueDistanceToVoorligger** : Dit is de werkelijke afstand tot het voorliggende voertuig in de simulatie. Het ACCS-systeem moet deze waarde meten met behulp van de Front Facing Radar Sensor.
- **TrueVoorliggerSpeed** : Dit is de werkelijke snelheid van het voorliggende voertuig in de simulatie. Deze waarde beïnvloedt de TrueDistanceToVoorligger en moet op de achtergrond worden bijgehouden in de simulatie.
- **TrueVehicleAcceleration** : Dit is de werkelijke verandering (remmen of gasgeven) van TrueVehicleSpeed in de simulatie. Dit is de waarde die door de Gaspedaal/Remsysteem monads wordt aangepast.

Door deze externe componenten in de simulatie te implementeren, kan het ACCS-systeem worden getest en gevalideerd onder realistische omstandigheden. Het systeem moet in staat zijn om deze "echte wereld" variabelen te meten en erop te reageren om effectief de snelheid van het voertuig en de afstand tot het voorliggende voertuig te regelen.

# Architectuurschetsen:
## Hardware:

De hardware-architectuur bestaat uit de volgende componenten en verbindingen:

- WheelSpeedSensor (Infineon TLE5041plusC): Meet de veranderingen van het magnetisch veld van de wielen,de frequentie van deze veranderingen hangt af van TrueVehicleSpeed. Deze sensor stuurt deze door naar de MeasuredSpeedCalculator.
- MeasuredSpeedCalculator (C++ code met python Bindings.): Berekent de MeasuredSpeed op basis van de WheelSpeedSensor, Wieldiameter, CPR van het encoderwiel. Stuurt de MeasuredSpeed door naar de CPU.
- Front Radar Sensor (Bosch Front Radar): Meet de afstand tot het voorliggende voertuig en stuurt deze informatie door naar de CPU.
- CPU: Verwerkt de gegevens van de Wheel Speed Sensor en Front Radar Sensor, en stuurt commando's naar de actuatoren.
- Gaspedaal: Ontvangt commando's van de CPU om de acceleratie van het voertuig te regelen.
- Remsysteem: Ontvangt commando's van de CPU om het afremmen van het voertuig te regelen.

```mermaid
graph TB 
A[WheelSpeedSensor- TLE5041plusC]
B[VehicleSpeedCalculator - C++ code]
F[FrontRadarSensor]
C((CPU))
D[Gaspedaal]
E[Remsysteem]
    subgraph Sensors
        subgraph VehicleSpeedSensor 
        A ==>|CurrentModulation| B
    end
    F
    end
    B ==> C
    F ==> C
        C --> D
        C --> E
    subgraph Actuators
    D
    E
    end
    ", height = '200%', width = '140%')

```

- De WheelSpeedSensor zit via 12v current Modulation interface verbonden met de MeasuredSpeedCalculator.
- De Front Radar Sensor en de MeasuredSpeedCalculator zijn verbonden met de CPU via een bekabelde interface.
- De CPU communiceert via een bekabelde interface met de Gaspedaal en Remsysteem actuatoren om de snelheid van het voertuig te regelen om zo een veilige afstand tot het voorliggende voertuig te behouden.




## Software:
De software bestaat uit verschillende klassen die de sensoren, actuatoren, CPU en algoritmes voor ACCS bevatten. De interfaces tussen de klassen zijn gedefinieerd om gegevens uit te wisselen en de algehele werking van het systeem te coördineren. Het regelsysteem is geïmplementeerd volgens het Functional Reactive Programming principe en is geschreven in Python, met gebruik van de C++-bibliotheek voor de SpeedSensor.


## Verdere abstractie voor gaspedaal/remsysteem
Waarchijnlijk is het voor het implementeren makkelijker om acceleratie/deacceleratie als een functie te zien, waar deacceleratie negative acceleratie is.
Er komt dan nog tussen de CPU en het remsysteem en gaspedaal ongeveer het volgende stukje code (abstraction interface achtig onderdeel). 

```haskell

RemmenOfGasgeven :: (Num a, Ord a) => (a -> b) -> (a -> b) -> a -> b
RemmenOfGasgeven rempedaal gaspedaal a
  | a <= 0    = rempedaal a
  | otherwise = gaspedaal a

```

In dit geval zit de logica/berekening van *Acceleration in $m/s^2$* naar *GaspedaalPercentage int:(range 0,100)* nog in de  `gaspedaal a ` functie.


### Diagram


#  ```mermaid
# classDiagram
#     class WheelSpeedSensor {
#         +measureOutputCurrent(): float
#     }
#     class MeasuredSpeedCalculator {
# 				-WHEEL_DIAMETER:float
# 				-ENCODER_WHEEL_CPR:int
#         +calculateVehicleSpeed(WheelSpeedSensorOutputCurrent: float, wheel_diameter: float, cpr: int): float
#     }
#     class MeasuredSpeedSensor {
#         +getMeasuredSpeed(): float
#     }
#     class FrontRadarSensor {
#         +measureDistanceToFrontVehicle(): float
#     }
#     class GasPedaal {
#         +PressGasPedaal(percentage:int): void
#         -MAX_ACCELERATION: float
#     }
#     class RemSysteem {
#         +PressRemPedaal(percentage:int): void
#         -MAX_DECELERATION: float
#     }
#     class FunctionalCPU {
#         +calculateNewAcceleration(vehicle_speed: float, distance_to_front_vehicle: float, max_acceleration: float, seconds_distance_to_vehicle_in_front: float): float
#         +calculateNewDeceleration(vehicle_speed: float, distance_to_front_vehicle: float, max_deceleration: float, seconds_distance_to_vehicle_in_front: float): float
#         -DESIRED_SECONDS_TO_VEHICLE_IN_FRONT: float
#     }
#     class RemmenOfGasgeven {
#         +adjustAcceleration(acceleration: float): void
#     }
#     MeasuredSpeedSensor *-- WheelSpeedSensor : Composition
#     MeasuredSpeedSensor *-- MeasuredSpeedCalculator : Composition
#     WheelSpeedSensor -- MeasuredSpeedCalculator : Association
#     MeasuredSpeedSensor ..> FunctionalCPU : Dependency
#     FrontRadarSensor ..> FunctionalCPU : Dependency
#     FunctionalCPU ..> RemmenOfGasgeven : Dependency
#     RemmenOfGasgeven -- GasPedaal : Association
#     RemmenOfGasgeven -- RemSysteem : Association
#    ", height = '100%', width = '100%')

```


1. **WheelSpeedSensor** : Deze klasse is verantwoordelijk voor het meten van de wielsnelheid(eigenlijk aleen Hall Effect). Het bevat een methode `measureOutputCurrent()` die de uitgangsstroom van de sensor meet.
2. **MeasuredSpeedCalculator** : Deze klasse ontvangt de uitgangsstroom van de WheelSpeedSensor en berekent de voertuigsnelheid op basis van de wielsnelheid en andere constanten zoals WHEEL_DIAMETER en ENCODER_WHEEL_CPR. De berekening gebeurt in de methode `calculateVehicleSpeed()`.
3. **MeasuredSpeedSensor** : Deze klasse is verantwoordelijk voor het verkrijgen van de gemeten snelheid van het voertuig. Het bevat een methode `getMeasuredSpeed()` die de gemeten voertuigsnelheid retourneert.
4. **FrontRadarSensor** : Deze klasse meet de afstand tot het voorliggende voertuig. Deze waarde wordt vervolgens doorgegeven aan de FunctionalCPU klasse.
5. **GasPedaal** : Deze klasse regelt de acceleratie van het voertuig. Het ontvangt de berekende acceleratie van de RemmenOfGasgeven klasse en past deze toe op het voertuig. De klasse heeft een private variabele MAX_ACCELERATION, die de maximale acceleratieconstante in m/s² bevat.
6. **RemSysteem** : Deze klasse regelt het afremmen van het voertuig. Het ontvangt de berekende vertraging van de RemmenOfGasgeven klasse en past deze toe op het voertuig. De klasse heeft een private variabele MAX_DECELERATION, die de maximale vertragingconstante (remmen) in m/s² bevat.
7. **FunctionalCPU** : Deze klasse bevat twee methoden, `calculateNewAcceleration()` en `calculateNewDeceleration()`. Deze methoden nemen respectievelijk de voertuigsnelheid, afstand tot het voorliggende voertuig, maximale acceleratie/deceleratie en seconden afstand tot het voorliggende voertuig als parameters en berekenen de nieuwe acceleratie of vertraging, om zo dichter bij de gewenste afstand tot de voorligger te komen. De klasse heeft een private variabele DESIRED_SECONDS_TO_VEHICLE_IN_FRONT, die de minimale veilige tijd aangeeft om een veilige afstand te behouden tussen het voertuig en het voorliggende voertuig.
8. **RemmenOfGasgeven** : Deze klasse is verantwoordelijk voor het aanpassen van de acceleratie van het voertuig op basis van de berekende waarden van de FunctionalCPU klasse. Het bevat een methode `adjustAcceleration()` die de acceleratie aanpast.

De relaties tussen de verschillende klassen: 

- MeasuredSpeedSensor heeft een compositierelatie met WheelSpeedSensor en MeasuredSpeedCalculator. (Bestaat uit deze Twee Subsensors)
- WheelSpeedSensor heeft een associatierelatie met MeasuredSpeedCalculator. (de Calculator moet elke keer de measureOutputCurrent() method aanroepen)
- MeasuredSpeedSensor, FrontRadarSensor en FunctionalCPU hebben dependancyrelaties. (dependancyrelaties zijn mischien niet helemaal 'correct' maar omdat dit functioneele stukken code zijn, weergeeft deze relatie de functionele inputs) 
- RemmenOfGasgeven heeft associatierelaties met GasPedaal en RemSysteem. (Het GasPedaal en RemSysteem moeten opvragen wat de dubbelzinnige acceleration waarde betekend in de RemmenOfGasgeven (positief of negatief))

## Flowchart

### Diagram
```{r,echo=FALSE, results = "asis"}
library(DiagrammeR)
library(networkD3)
library(webshot2)

k  <- mermaid("
graph TB
A[WheelSpeedSensor - TLE5041plusC]
B[MeasuredSpeedCalculator - C++ code]
F[FrontRadarSensor]
C[FunctionalCPU]
D[GasPedaal]
E[RemSysteem]
subgraph Sensors
    subgraph VehicleSpeedSensor
        A -->|CurrentModulation| B
    end
    F
end
B --> C
F --> C
subgraph FunctionalCPU
    C
end
C --> D
C --> E
subgraph Actuators
    D
    E
end
    ", height = '200%', width = '140%')

saveNetwork(k, "k.html")

webshot("k.html", file = "k.png",vwidth = 650) 
```

