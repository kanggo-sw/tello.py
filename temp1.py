from lib.tello.swarm import Tello # Import Tello 

my_tellos = list() 
my_tellos.append('0TQDFCAABBCCDD') # Replace with your Tello Serial Number 
my_tellos.append('0TQDFCAABBCCEE') # Replace with your Tello Serial Number 

with Tello(my_tellos) as fly: # Use Tello as a Context Manager to ensure safe landing in case of any errors 
    fly.takeoff() # Single command for all Tellos to take-off 
    fly.forward(50) # Single command for all Tellos to fly forward by 50cm 
    
    with fly.sync_these(): # Keep the following commands in-sync, even with different commands for each Tello 
        fly.left(30, tello=1) # Tell just Tello1 to fly left 
        fly.right(30, tello=2) # At the same time, Tello2 will fly right 
    
    fly.flip(direction='forward') # Flips are easy to perform via the Tello SDK 
    fly.land() 
