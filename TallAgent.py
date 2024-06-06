from typing import List, Tuple

import numpy as np
from Agent import Player
import random
from enum import Enum


ADJACENCY_ARRAY = np.array([
    [],  # Empty list for territory ID 0 (assuming territory IDs start from 1)
    [43, 3, 5, 4],
    [],  # Empty list for territory ID 2
    [14, 6, 5, 1],
    [43, 1, 5, 7],
    [1, 3, 6, 7, 8, 4],
    [3, 5, 8],
    [8, 5, 4, 9],
    [5, 6, 7, 9],
    [7, 8, 10],
    [9, 11, 12],
    [10, 12, 13, 21],
    [10, 11, 13],
    [11, 12],
    [3, 15, 16],
    [14, 16, 17, 20],
    [14, 15, 17, 18],
    [16, 15, 20, 19, 18],
    [16, 17, 19, 21],
    [17, 18, 20, 21, 22, 35],
    [15, 17, 19, 27, 31, 35],
    [18, 19, 22, 23, 24, 11],
    [19, 21, 35, 23],
    [21, 22, 35, 24, 25, 26],
    [21, 23, 25],
    [24, 23, 26],
    [23, 25],
    [20, 31, 37, 28],
    [27, 37, 33, 32, 29],
    [28, 32, 30],
    [29, 32, 34, 43],
    [27, 37, 36, 35, 20],
    [29, 30, 34, 33, 28],
    [28, 32, 34, 37],
    [33, 32, 30],
    [31, 36, 22, 23, 19, 20],
    [35, 38, 37, 31],
    [38, 36, 33, 31, 27, 28],
    [37, 36, 39],
    [40, 41, 38],
    [39, 41, 42],
    [39, 42, 40],
    [41, 40],
    [30, 1, 4]
], dtype=object)

class TallAgent(Player):
    def make_selection(self, available_territories: List['Territory']) -> 'Territory':
        return random.choice(available_territories)

    def add_infantry(self) -> 'Territory':
        if not self.personal_territories:
            return None
        territory = random.choice(list(self.personal_territories.values()))
        return territory

    def reinforce(self, total_reinforcements : int ) -> List[Tuple['Territory', int]]:
        print(total_reinforcements, "total")
        reinforcement_allocation = []

        max_troops_territory = max(self.personal_territories.values(), key=lambda t: t.troop_count)
        print(max_troops_territory.troop_count,"-pre reinforce")

        for neighbours in ADJACENCY_ARRAY[max_troops_territory.id]:
            if neighbours not in self.personal_territories:
                reinforcement_allocation = [(max_troops_territory, total_reinforcements)]
                print(1, "   ", reinforcement_allocation)
                return reinforcement_allocation



        if self.personal_territories:
            selected_territory_id = random.choice(list(self.personal_territories.keys()))
            selected_territory = self.personal_territories[selected_territory_id]
            reinforcement_allocation = [(selected_territory, total_reinforcements)]

        return reinforcement_allocation

    def invade(self, adjacent_territories: List[Tuple['Territory', List['Territory']]]) -> Tuple['Territory', 'Territory', int]:
        max_troops_territory = max(self.personal_territories.values(), key=lambda t: t.troop_count)
        print(max_troops_territory.troop_count,"--pre invade-")
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


        sorted_territories = sorted(self.personal_territories.values(), key=lambda t: t.troop_count, reverse=True)
        print(sorted_territories[0].troop_count, "++++++", sorted_territories[1].troop_count)
        if len(sorted_territories)>2:
            for neighbours in ADJACENCY_ARRAY[sorted_territories[0].id]:
                if neighbours not in self.personal_territories:
                    if (sorted_territories[0],sorted_territories[1]) in valid_manoeuverable_territories:
                        num_troops = sorted_territories[1].troop_count - 1
                        return sorted_territories[1], sorted_territories[0], num_troops
                    elif (sorted_territories[0],sorted_territories[2]) in valid_manoeuverable_territories:
                        num_troops = sorted_territories[2].troop_count - 1
                        return sorted_territories[2], sorted_territories[0], num_troops


        # Pick a random source territory and its list of reachable territories
        source_territory, reachable_territories = random.choice(valid_manoeuverable_territories)

        # Pick a random destination territory from the reachable territories
        destination_territory = random.choice(reachable_territories)

        # Decide to move a random number of troops (up to the number of troops in the source territory - 1)
        num_troops = random.randint(1, source_territory.troop_count - 1)

        return source_territory, destination_territory, num_troops

    def get_player_name(self):
        return (f"Tall Agent {self.id}")
