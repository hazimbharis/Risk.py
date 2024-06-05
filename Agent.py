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


ADJACENCY_LIST = {
    1: [43, 3, 5, 4],
    3: [14, 6, 5, 1],
    4: [43, 1, 5, 7],
    5: [1, 3, 6, 7, 8, 4],
    6: [3, 5, 8],
    7: [8, 5, 4, 9],
    8: [5, 6, 7, 9],
    9: [7, 8, 10],
    10: [9, 11, 12],
    11: [10, 12, 13, 21],
    12: [10, 11, 13],
    13: [11, 12],
    14: [3, 15, 16],
    15: [14, 16, 17, 20],
    16: [14, 15, 17, 18],
    17: [16, 15, 20, 19, 18],
    18: [16, 17, 19, 21],
    19: [17, 18, 20, 21, 22, 35],
    20: [15, 17, 19, 27, 31, 35],
    21: [18, 19, 22, 23, 24, 11],
    22: [19, 21, 35, 23],
    23: [21, 22, 35, 24, 25, 26],
    24: [21, 23, 25],
    25: [24, 23, 26],
    26: [23, 25],
    27: [20, 31, 37, 28],
    28: [27, 37, 33, 32, 29],
    29: [28, 32, 30],
    30: [29, 32, 34, 43],
    31: [27, 37, 36, 35, 20],
    32: [29, 30, 34, 33, 28],
    33: [28, 32, 34, 37],
    34: [33, 32, 30],
    35: [31, 36, 22, 23, 19, 20],
    36: [35, 38, 37, 31],
    37: [38, 36, 33, 31, 27, 28],
    38: [37, 36, 39],
    39: [40, 41, 38],
    40: [39, 41, 42],
    41: [39, 42, 40],
    42: [41, 40],
    43: [30, 1, 4]
}


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
        self.cards = []

    def reset(self):
        self.personal_territories = {}
        self.cards = []
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

    def get_card_sets(self) -> int:
        infantry_count = sum(1 for card in self.cards if card.type == "Infantry")
        cavalry_count = sum(1 for card in self.cards if card.type == "Cavalry")
        artillery_count = sum(1 for card in self.cards if card.type == "Artillery")
        wild_count = sum(1 for card in self.cards if card.type == "Wild")

        sets = min(infantry_count, cavalry_count, artillery_count)
        sets += wild_count

        return sets

    def remove_card_sets(self, sets: int) -> None:
        infantry_cards = [card for card in self.cards if card.type == "Infantry"]
        cavalry_cards = [card for card in self.cards if card.type == "Cavalry"]
        artillery_cards = [card for card in self.cards if card.type == "Artillery"]
        wild_cards = [card for card in self.cards if card.type == "Wild"]

        for _ in range(sets):
            if infantry_cards:
                self.cards.remove(infantry_cards.pop())
            if cavalry_cards:
                self.cards.remove(cavalry_cards.pop())
            if artillery_cards:
                self.cards.remove(artillery_cards.pop())
            if wild_cards:
                self.cards.remove(wild_cards.pop())

    def calculate_reinforcement(self, unit_cap: int = 130) -> int:
        # Base reinforcement based on the number of territories
        reinforcement_count = max(3, math.floor(len(self.personal_territories) / 3))

        # Add region bonuses if the player owns all territories in the region
        for region, bonus in REGION_BONUSES.items():
            if self.owns_all_territories_in_region(region):
                reinforcement_count += bonus

        # Trade in cards if possible
        card_sets = self.get_card_sets()
        if card_sets > 0:
            reinforcement_count += card_sets * 6

        total_units = self.unassigned_units + sum(territory.troop_count for territory in self.personal_territories.values())

        if total_units + reinforcement_count >= unit_cap:
            reinforcement_count = 0
        # print(reinforcement_count)
        return reinforcement_count

    def remove_player_units(self, number_of_units: int) -> None:
        if number_of_units > 0:
            self.unassigned_units -= number_of_units
        return None

    def reset_player_units(self):
        self.unassigned_units = 0

    def owns_all_territories_in_region(self, region):
        region_territories = Region[region.name].value
        return all(territory_id in self.personal_territories for territory_id in region_territories)

    def add_card(self, card):
        self.cards.append(card)

    # Abstract
    def get_player_name(self):
        return (self.id)

    # Abstract
    def make_selection(self, available_territories: List['Territory']) -> 'Territory':
        pass

    # Abstract Define yourself
    def add_infantry(self) -> 'Territory':
        pass

    # Abstract
    def reinforce(self) -> List[Tuple['Territory', int]]:
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

    def reinforce(self) -> List[Tuple['Territory', int]]:
        total_reinforcements = self.calculate_reinforcement()
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
