# finnff ATP Bezem 22/23

## Project- en Testplan

* zie /projectTestPlan/

## Eindopdracht Testrapport
zie hiervoor [tests/README.md](https://github.com/finnff/ATP2022/blob/main/tests/README.md)

---

## Eindopdracht

### Requirements:

* redis-server

###  Redis controller './redis-memory-remote'

Redis is een RAM based key-value store dat we gebruiken voor inter-process communication in onze simulator Regelsysteem. (Websockets was te langzaam/onstabiel)

Alle data is opgeslagen in RAM voor snelle read write performance, maar Redis heeft persistence features, dus deze data wordt gesaved naar Harddrive blijft bestaan na sluiten applicatie of na reboots. Hiervoor heb ik een Tool gemaakt:

#### Usage:

1. `chmod +x redis-memory-remote`
2. `./redis-memory-remote`

- **View Data**: Interactive UI to browse Redis keys, use `arrow keys, Enter and Esc`
- **Reset Data**: Reset keys to default values. `Shift+R` or from cli:  `./redis-memory-remote -R`
- **Flush Data**: (__Unstable!__) Remove all data from Redis. `Shift+F` or from cli:  `./redis-memory-remote -F`

Note: Flush (basically SQL Droptable) heeft nogal de neiging om raceconditions en crashes te veroorzaken zeker voor de C++ binding dus het is meestal voldoende om tijdens runnen aleen te reseten naar default Waardes voor de simulator/testing 

