#!/usr/bin/env python3
# Python 3.6

# Import the Halite SDK, which will let you interact with the game.
import hlt

# This library contains constant values.
from hlt import constants

# This library contains direction metadata to better interface with the game.
from hlt.positionals import Direction
import random

# Logging allows you to save messages for yourself. This is required because the regular STDOUT
#   (print statements) are reserved for the engine-bot communication.
import logging

""" <<<Game Begin>>> """

# This game object contains the initial game state.
game = hlt.Game()
# At this point "game" variable is populated with initial map data.
# This is a good place to do computationally expensive start-up pre-processing.
# As soon as you call "ready" function below, the 2 second per turn timer will start.
game.ready("Padawan")

# Now that your bot is initialized, save a message to yourself in the log file with some important information.
#   Here, you log here your id, which you can always fetch from the game object by using my_id.
logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

ship_directives = {}

""" <<<Game Loop>>> """

while True:
    # This loop handles each turn of the game. The game object changes every turn, and you refresh that state by
    #   running update_frame().
    game.update_frame()
    # You extract player metadata and the updated map metadata here for convenience.
    me = game.me
    game_map = game.game_map

    # A command queue holds all the commands you will run this turn. You build this list up and submit it at the
    #   end of the turn.
    command_queue = []
    current_destinations = []
    # Check how much Halite is left on the board
    available_halite = game_map.count_halite_avail()     

    for ship in me.get_ships():

        # store status of ships by ID
        if ship.id not in ship_directives:
            ship_directives[ship.id] = "exploring"
        
        if ship_directives[ship.id] == "returning":
            if ship.position == me.shipyard.position:
                ship_directives[ship.id] = "exploring"
                command_queue.append(ship.move(ship.find_near_square_for_gathering(game_map, current_destinations)))
                continue
            else:
                move = game_map.naive_navigate(ship, me.shipyard.position)
                command_queue.append(ship.move(move))
                continue
        elif ship.halite_amount == constants.MAX_HALITE:
            ship_directives[ship.id] = "returning"
    
        # Check to see if Halite is low in position and ship is not full...
        # If Halite is less than 5% of current held ship amount...then move (low cost impact for movement)
        # Else stay still and mine....unless ship is full.... then need to move safely
        if game_map[ship.position].halite_amount <= .20 * ship.halite_amount and not ship.is_full or game_map[ship.position].halite_amount == 0:                    
            command_queue.append(ship.move(ship.find_near_square_for_gathering(game_map, current_destinations)))
        else:
            command_queue.append(ship.stay_still())

        logging.info(ship_directives[ship.id])

    # If the game is in the first 200 turns and you have enough halite, spawn a ship.
    # Don't spawn a ship if you currently have a ship at port, though - the ships will collide.
    if me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied and len(me.get_ships()) < 30:
        command_queue.append(me.shipyard.spawn())

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)

