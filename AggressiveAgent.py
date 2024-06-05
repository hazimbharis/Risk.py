from typing import List, Tuple
from Agent import Player


class RandomAgent(Player):

    def make_selection(self, available_territories: List['Territory']) -> 'Territory':
        pass

    def add_infantry(self) -> 'Territory':
        pass

    def reinforce(self) -> List[Tuple['Territory', int]]:
        pass

    def invade(self, adjacent_territories: List[Tuple['Territory', List['Territory']]]) -> Tuple['Territory', 'Territory', int]:
        pass
    def manoeuvre(self, manoeuverable_territories: List[Tuple['Territory', List['Territory']]]) -> Tuple['Territory', 'Territory', int]:
        pass
    def get_player_name(self):
        pass
