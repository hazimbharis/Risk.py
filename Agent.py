from collections import Counter
from enum import Enum
import math
from typing import List, Tuple
import random


class Colour(Enum):
    SEA = (0, 255, 255),
    WHITE = (255, 255, 255),
    BLACK = (0, 0, 0),
    RED = (200, 0, 0),
    BLUE = (0, 0, 255),
    GREEN = (0, 255, 0),
    RUST = (210, 150, 75),
    LIME = (180, 255, 100)




class Region(Enum):
    NORTH_AMERICA = frozenset({1, 3, 4, 5, 6, 7, 8, 9, 43})
    SOUTH_AMERICA = frozenset({10, 11, 12, 13})
    EUROPE = frozenset({14, 15, 16, 17, 18, 19, 20})
    AFRICA = frozenset({21, 22, 23, 24, 25, 26})
    ASIA = frozenset({27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38})
    AUSTRALIA = frozenset({39, 40, 41, 42})


REGION_BONUSES = {
    Region.NORTH_AMERICA: 5,
    Region.SOUTH_AMERICA: 2,
    Region.EUROPE: 5,
    Region.AFRICA: 3,
    Region.ASIA: 7,
    Region.AUSTRALIA: 2
}


class Player():
    def __init__(self, id: int, unassigned_units: int):
        self.id = id
        self.personal_territories = {}
        self.base_unassigned = unassigned_units
        self.unassigned_units = unassigned_units
        self.cards = [0, 0, 0]
        self.personal_territories_hash = ""
        self.manoeuvreable_tiles = {}
        self.adjacent_territories_cache = []
        self.base_reinforcement = 3
        
        self.card_value_dict = {
                               0:5,
                               1:6,
                               2:7,
                               3:10
                               }

    def reset(self):
        self.personal_territories = {}
        self.cards = [0, 0, 0]
        self.unassigned_units = self.base_unassigned

    def get_colour(self) -> tuple:
        player_colour_dict = {
            0: Colour.RED,
            1: Colour.BLUE,
            2: Colour.GREEN,
            3: Colour.RUST,
            4: Colour.LIME
        }
        return (player_colour_dict[self.id].value)

    def give_player_territory(
            self,
            territory: 'Territory',
            num_units: int
    ) -> None:
        if num_units > 0:

            self.personal_territories[territory.id] = territory
            territory.owner = self
            territory.set_troop_count(num_units)
            return None
        else:
            raise ArithmeticError

    def remove_player_territory(self, territory: 'Territory') -> None:
        del self.personal_territories[territory.id]
        return None

    def give_player_units(self, number_of_units: int, ) -> None:
        if number_of_units > 0:
            self.unassigned_units += number_of_units

        return None
    
    def get_card_set(self) -> int:
            
        max_count = max(self.cards)
        if max_count > 3:
            return self.cards.index(max_count)
        
        if self.cards[0] > 0 and self.cards[1] > 0 and self.cards[0] > 0:
            return 3    
        return -1
        

    def remove_card_set(self, set: int) -> None:
        if set == 1 or set == 2 or set == 3:
            self.cards[set-1] -= 3
        else:
            for x in range(len(self.cards)):
                self.cards[x] -= 1 
        

    def calculate_reinforcement(self, changed : bool ,  unit_cap: int = 130) -> int:
        # Base reinforcement based on the number of territories

        if changed:
            reinforcement_count = max(3, math.floor(len(self.personal_territories) / 3))

            # Add region bonuses if the player owns all territories in the region
            owned_regions = {region for region in Region if self.owns_all_territories_in_region(region)}
            reinforcement_count += sum(REGION_BONUSES[region] for region in owned_regions)
            self.base_reinforcement = reinforcement_count
        else:
            reinforcement_count = self.base_reinforcement

        
        # Trade in cards if possible
        card_set_num = self.get_card_set()
        if card_set_num != -1:
            
            card_value = self.card_value_dict[card_set_num]
            reinforcement_count += card_value
            self.remove_card_set(card_set_num)

        total_units = self.unassigned_units + sum(territory.troop_count for territory in self.personal_territories.values())


        if total_units + reinforcement_count >= unit_cap:
            reinforcement_count = 0

        return reinforcement_count
    
    def personal_territories_changed(self):
        
        if hash(frozenset(set(self.personal_territories))) != self.personal_territories_hash:
            self.personal_territories_hash = hash(frozenset(set(self.personal_territories)))
            return True
        else:
            
            return False
        

    def remove_player_units(self, number_of_units : int) -> None:
        if number_of_units > 0:
            self.unassigned_units -= number_of_units
        return None

    def reset_player_units(self):
        self.unassigned_units = 0

    def owns_all_territories_in_region(self, region):
        return region.value.issubset(self.personal_territories)

    
    

    def add_card(self):
        index = random.randint(0, len(self.cards) - 1)
        self.cards[index] += 1
        

    # Abstract
    def get_player_name(self):
        return (self.id)

    # Abstract
    def make_selection(self, available_territories: List['Territory']) -> 'Territory':
        pass

    # Abstract Define yourself
    def add_infantry(self) -> 'Territory':
        pass

    #Abstract
    def reinforce(self, total_reinforcements : int ) -> List[Tuple['Territory', int]]:
        pass

    # Abstract
    def invade(self, adjacent_territories: List[Tuple['Territory', List['Territory']]]) -> Tuple['Territory', 'Territory', int]:
        pass

    # Abstract
    def manoeuvre(self, manoeuverable_territories: List[Tuple['Territory', List['Territory']]]) -> Tuple['Territory', 'Territory', int]:
        pass


class RandomAgent(Player):
    def make_selection(self, available_territories: List['Territory']) -> 'Territory':
        return random.choice(available_territories)

    def add_infantry(self) -> 'Territory':
        if not self.personal_territories:
            return None
        territory = random.choice(list(self.personal_territories.values()))
        return territory

    def reinforce(self, total_reinforcements : int ) -> List[Tuple['Territory', int]]:
       
        reinforcement_allocation = []

        if self.personal_territories:
            selected_territory_id = random.choice(list(self.personal_territories.keys()))
            selected_territory = self.personal_territories[selected_territory_id]
            reinforcement_allocation = [(selected_territory, total_reinforcements)]

        return reinforcement_allocation

    def invade(self, adjacent_territories: List[Tuple['Territory', List['Territory']]]) -> Tuple['Territory', 'Territory', int]:
        max_troops_territory = max(self.personal_territories.values(), key=lambda t: t.troop_count)

        if max_troops_territory.troop_count <= 3:
            return None

        adjacent_enemy_territories = []
        for territory, adjacents in adjacent_territories:
            if territory == max_troops_territory:
                for adjacent in adjacents:
                    if adjacent.get_owner().id != self.id:
                        adjacent_enemy_territories.append(adjacent)

        if not adjacent_enemy_territories:
            return None

        min_troops_enemy_territory = min(adjacent_enemy_territories, key=lambda t: t.troop_count)
        troops_to_use = max_troops_territory.troop_count - 1

        return max_troops_territory, min_troops_enemy_territory, troops_to_use


    def manoeuvre(self, manoeuverable_territories: List[Tuple['Territory', List['Territory']]]) -> Tuple['Territory', 'Territory', int]:
        # Filter out territories that don't have enough troops to manoeuvre
        valid_manoeuverable_territories = [
            (source, targets) for source, targets in manoeuverable_territories
            if source.troop_count > 1 and targets
        ]

        if not valid_manoeuverable_territories:
            return None, None, 0  # Indicating no valid manoeuvre available

        # Pick a random source territory and its list of reachable territories
        source_territory, reachable_territories = random.choice(valid_manoeuverable_territories)

        # Pick a random destination territory from the reachable territories
        destination_territory = random.choice(reachable_territories)

        # Decide to move a random number of troops (up to the number of troops in the source territory - 1)
        num_troops = random.randint(1, source_territory.troop_count - 1)

        return source_territory, destination_territory, num_troops

    def get_player_name(self):
        return (f"Random Agent {self.id}")
