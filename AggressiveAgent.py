from typing import List, Tuple
from Agent import Player
import random
from enum import Enum


class AggressiveAgent(Player):

    def make_selection(self, available_territories: List['Territory']) -> 'Territory':
        class Continent(Enum):
            NORTH_AMERICA = 1
            SOUTH_AMERICA = 2
            EUROPE = 3
            AFRICA = 4
            ASIA = 5
            AUSTRALIA = 6
        choice = random.choice(available_territories)
        print(choice.name)
        print(choice.id)
        print(choice.continent)
        # Get available territories in each continent
        # Initialize empty array to store territories
        continents = []
        for i in range(6):
            continents.append([])
        # Store each territory in respective array corresponding to a continent
        for t in available_territories:
            continents[t.continent.value-1].append(t)

        # Create arbitrary ranks of continents
        if len(continents[Continent.NORTH_AMERICA.value-1]) > 0:
            choice = random.choice(continents[Continent.NORTH_AMERICA.value-1])
        elif len(continents[Continent.SOUTH_AMERICA.value-1]) > 0:
            choice = random.choice(continents[Continent.SOUTH_AMERICA.value-1])
        elif len(continents[Continent.AUSTRALIA.value-1]) > 0:
            choice = random.choice(continents[Continent.AUSTRALIA.value-1])
        elif len(continents[Continent.AFRICA.value-1]) > 0:
            choice = random.choice(continents[Continent.AFRICA.value-1])
        elif len(continents[Continent.EUROPE.value-1]) > 0:
            choice = random.choice(continents[Continent.EUROPE.value-1])
        elif len(continents[Continent.ASIA.value-1]) > 0:
            choice = random.choice(continents[Continent.ASIA.value-1])

        # Min / max fraction

        # input("Enter to continue")
        return choice

    def add_infantry(self) -> 'Territory':
        if not self.personal_territories:
            return None
        territory = random.choice(list(self.personal_territories.values()))
        print("Add infantry: " + territory.name)
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
        return (f"Aggressive Agent {self.id}")
