python "%SUMO_HOME%\tools\randomTrips.py" -n osm.net.xml -p 6 -o osm.passenger.trips.xml -r osm.passenger.rou.xml -e 3600 --vehicle-class passenger --vclass passenger -s --prefix veh --min-distance 50  --lanes --validate 


python "%SUMO_HOME%\tools\randomTrips.py" -n osm.net.xml -o osm.trips.xml   -r test.rou.xml