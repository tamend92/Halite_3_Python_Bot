import abc
import random

from . import commands, constants
from .positionals import Direction, Position
from .common import read_input

class Entity(abc.ABC):
    """
    Base Entity Class from whence Ships, Dropoffs and Shipyards inherit
    """
    def __init__(self, owner, id, position):
        self.owner = owner
        self.id = id
        self.position = position

    @staticmethod
    def _generate(player_id):
        """
        Method which creates an entity for a specific player given input from the engine.
        :param player_id: The player id for the player who owns this entity
        :return: An instance of Entity along with its id
        """
        ship_id, x_position, y_position = map(int, read_input().split())
        return ship_id, Entity(player_id, ship_id, Position(x_position, y_position))

    def __repr__(self):
        return "{}(id={}, {})".format(self.__class__.__name__,
                                      self.id,
                                      self.position)

class Dropoff(Entity):
    """
    Dropoff class for housing dropoffs
    """
    pass


class Shipyard(Entity):
    """
    Shipyard class to house shipyards
    """
    def spawn(self):
        """Return a move to spawn a new ship."""
        return commands.GENERATE


class Ship(Entity):
    """
    Ship class to house ship entities
    """
    def __init__(self, owner, id, position, halite_amount):
        super().__init__(owner, id, position)
        self.halite_amount = halite_amount
        

    @property
    def is_full(self):
        """Is this ship at max halite capacity?"""
        return self.halite_amount >= constants.MAX_HALITE

    def make_dropoff(self):
        """Return a move to transform this ship into a dropoff."""
        return "{} {}".format(commands.CONSTRUCT, self.id)

    def move(self, direction):
        """
        Return a move to move this ship in a direction without
        checking for collisions.
        """
        raw_direction = direction
        if not isinstance(direction, str) or direction not in "nsewo":
            raw_direction = Direction.convert(direction)
        return "{} {} {}".format(commands.MOVE, self.id, raw_direction)

    def can_move(self, game_map):
        """
        Returns boolean value determining if resources available to move
        checks current square
        """
        if game_map[self.position].halite_amount * .10 > self.halite_amount: 
            return False 
        else: 
            return True

    def stay_still(self):
        """
        Don't move this ship.
        """
        return "{} {} {}".format(commands.MOVE, self.id, commands.STAY_STILL)
    
    def find_near_square_for_gathering(self, game_map, current_destinations):
        """
        Checks surrounding squares from the ship searching for optimal move
        Compares squares by most_halite and sets ==
        empty_spaces list stores index number of empty surrounding cardinals, which allows for randomization of direction
        need to improve this, but it is a start for bot V1
        """
        empty_spaces = []

        surrounding_squares = self.position.get_surrounding_cardinals()
        
        position_directions = Direction.get_all_cardinals()

        most_halite = 0

        selected_direction = -1

        for counter, square in enumerate(surrounding_squares):
            if game_map[square].halite_amount > most_halite and not game_map[square].is_occupied:
                most_halite = game_map[square].halite_amount
               
                selected_direction = counter

                empty_spaces.append(counter)
        
        # If direction still not selected...choose a random direction to go that's empty
        if selected_direction == -1:
            # Check to make sure there are empty spaces
            if not len(empty_spaces) == 0:
                return position_directions[random.choice(empty_spaces)]
            else:
                return Direction.Still
        else:
            current_destinations.append(position_directions[selected_direction])
            return position_directions[selected_direction]

    @staticmethod
    def _generate(player_id):
        """
        Creates an instance of a ship for a given player given the engine's input.
        :param player_id: The id of the player who owns this ship
        :return: The ship id and ship object
        """
        ship_id, x_position, y_position, halite = map(int, read_input().split())
        return ship_id, Ship(player_id, ship_id, Position(x_position, y_position), halite)

    def __repr__(self):
        return "{}(id={}, {}, cargo={} halite)".format(self.__class__.__name__,
                                                       self.id,
                                                       self.position,
                                                       self.halite_amount)
