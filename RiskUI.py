

from collections import deque
from enum import Enum
import time
import pygame
import sys
from typing import List, Dict, Tuple
import random


from Agent import RandomAgent, Player


class Continent(Enum):
    NORTH_AMERICA = 1,
    SOUTH_AMERICA = 2,
    EUROPE = 3,
    AFRICA = 4,
    ASIA = 5,
    AUSTRALIA = 6

class Stage(Enum):
    SELECTION = 1,
    PLACEMENT = 2,

class Colour(Enum):
    SEA = (0,255,255),
    WHITE = (255, 255, 255),
    BLACK = (0, 0, 0),
    RED = (200, 0, 0),
    BLUE = (0, 0, 255),
    GREEN = (0, 255, 0),
    RUST = (210,150,75),
    LIME = (180,255,100)

ADJACENCY_LIST = {
    
    1: [43,3,5,4],
    3: [14,6,5,1],
    4: [43,1,5,7],
    5: [1,3,6,7,8,4],
    6: [3,5,8],
    7: [8,5,4,9],
    8: [5,6,7,9],
    9: [7,8,10],
    10: [9,11,12],
    11: [10,12,13,21],
    12: [10,11,13],
    13: [11,12],
    14: [3,15,16],
    15: [14,16,17,20],
    16: [14,15,17,18],
    17: [16,15,20,19,18],
    18: [16,17,19,21],
    19: [17,18,20,21,22,35],
    20: [15,17,19,27,31,35],
    21: [18,19,22,23,24,11],
    22: [19,21,35,23],
    23: [21,22,35,24,25,26],
    24: [21,23,25],
    25: [24,23,26],
    26: [23,25],
    27: [20,31,37,28],
    28: [27,37,33,32,29],
    29: [28,32,30],
    30: [29,32,34,43],
    31: [27,37,36,35,20],
    32: [29,30,34,33,28],
    33: [28,32,34,37],
    34: [33,32,30],
    35: [31,36,22,23,19,20],
    36: [35,38,37,31],
    37: [38,36,33,31,27,28],
    38: [37,36,39],
    39: [40,41,38],
    40: [39,41,42],
    41: [39,42,40],
    42: [41,40],
    43: [30,1,4]
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

x_width_multiplier = 1.3
y_height_multiplier = 1.5

WIDTH, HEIGHT = 800*x_width_multiplier, 600*y_height_multiplier


class Card:
    def __init__(self, type):
        self.type = type





    
    

class Territory():
    def __init__(self, name : str, x_pos : int, y_pos : int, continent: Continent, id : int):
        self.name = name
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.continent = continent
        self.owner = None
        self.troop_count = 0
        self.id = id

    def get_position(self) -> tuple:
        return( (self.x_pos,self.y_pos) )
    
    def get_owner(self) -> Player :
        return(self.owner)
    
    def set_owner(self, owner : Player) -> None:
        self.owner = owner
        return None
    
    def get_troop_count(self) -> int:
        return(self.troop_count)
    
    def set_troop_count(self, troop_count : int) -> None:
        self.troop_count = troop_count
        return None
    
    def increment_troop_count(self, troop_increment : int) -> None:
        if troop_increment>0:
            self.troop_count += troop_increment
            return None
        else:
            raise ArithmeticError()

    def decrement_troop_count(self, troop_decrement : int) -> None:
        if troop_decrement>0:
            self.troop_count -= troop_decrement
            return None
        else:
            raise ArithmeticError()
        
    def reset(self) -> None:
        self.owner = None
        self.troop_count = 0

        return None

        
    def attack(self, attacking_troops : int):
        
        if attacking_troops <= 0:
            raise ValueError("Attacking troops must be positive")
        
        if self.troop_count <= 0:
            raise ValueError("Defending territory has no troops")

        # Dice rolls
        attacker_dice = sorted([random.randint(1, 6) for _ in range(min(attacking_troops, 3))], reverse=True)
        defender_dice = sorted([random.randint(1, 6) for _ in range(min(self.troop_count, 2))], reverse=True)

        # Compare dice rolls
        for a_roll, d_roll in zip(attacker_dice, defender_dice):
            if a_roll > d_roll:
                self.troop_count -= 1
            else:
                attacking_troops -= 1

        # Check if the territory has been conquered
        if self.troop_count <= 0:
            return (True, attacking_troops)
        else:
            return (False, 0)
    
    def get_outline_colour(self) -> tuple:
        continent_colour_dict = {
            Continent.NORTH_AMERICA: (255,255,0), # Yellow
            Continent.SOUTH_AMERICA: (255,100,10), # Orange
            Continent.EUROPE: (0,0,100), # Blue 
            Continent.AFRICA: (205,245,255), # White
            Continent.ASIA: (0,255,0), # Green
            Continent.AUSTRALIA: (240,0,255) # Purple
        }
        return(continent_colour_dict[self.continent])
    
class Game():
    def __init__(self, players : List[Player], territories : Dict[Territory, int], simulating : bool  = False):
        self.drawing = Drawing()
        random.shuffle(players) # random.shuffle shuffles in-place.
        self.turn_order = players

        self.card_deck = self.create_card_deck()
        self.simulating = simulating
        self.territories = territories
        self.stored_players = players
        #self.start_turns(players)

    def create_card_deck(self):
        deck = [Card("Infantry")] * 14 + [Card("Cavalry")] * 14 + [Card("Artillery")] * 14 + [Card("Wild")] * 2
        random.shuffle(deck)
        return deck
    
    def reset_game(self):
        for territory in self.territories.values():
            territory.reset()

        for player in self.stored_players:
            player.reset()

    def play_game(self, players: List[Player] = None, max_turns: int = 200) -> int:
        self.reset_game()
        if players is None:
            players = self.stored_players
        players = self.selection(players)
        players = self.add_infantry(players)
        running = True
        turn_count = 0
        while running:
            # Create a new list to store active players
            active_players = []
            for player in players:
                if player.personal_territories:
                    active_players.append(player)
                    self.main_section(player)
                    #time.sleep(0.3)
        
            # Update the list of players with active players
            players = active_players
        
            # Check if there is only one player remaining or the maximum number of turns is reached
            if len(players) == 1 or turn_count >= max_turns:
                running = False
            
                # Count the number of territories each player has
                player_territory_count = {}
                for player in players:
                    player_territory_count[player.id] = len(player.personal_territories)
            
                # Find the player with the most territories
                max_territories_player = max(player_territory_count, key=player_territory_count.get)
                
            
               
            
                return max_territories_player
            if not self.simulating:
                self.drawing.draw_map(self.territories)
        
            turn_count += 1
    
        return None

    def selection(self, players : List[Player]) -> List[Player]: #I'm going to make this return the state of turns when it's done selection
        for x in range(len(territories.items())):
            current_player = players.pop(0)
            players.append(current_player) # Circular 


            available_territories = self.get_available_territories()
            selected_territory = current_player.make_selection(available_territories)
            current_player.give_player_territory(selected_territory, 1)
            current_player.remove_player_units(1)


        return players
    
    def get_available_territories(self) -> List[Territory]:
        available_territories = []
        for territory_id in territories:
            territory = territories[territory_id]
            if territory.get_owner() is None:
                available_territories.append(territory)

        return(available_territories)
    
    def add_infantry(self, players : List[Player]) -> List[Player]:
        iterations = players[0].unassigned_units * len(players)
        for x in range(iterations):
            
            current_player = players.pop(0)
            players.append(current_player) # Circular 

            selected_territory = current_player.add_infantry()
            selected_territory.increment_troop_count(1)
            current_player.remove_player_units(1)
        return players



    def main_section(self, player : Player) -> None:
        self.reinforce(player)
        self.invade(player)
        
        self.manoeuvre(player)
        

    def reinforce(self, player: Player) -> None:
        reinforcement_count = player.calculate_reinforcement()
        
        player.give_player_units(reinforcement_count)
        reinforcement_tuples = player.reinforce()

        # Verify that the total number of reinforcements does not exceed the allowed reinforcement count
        total_reinforcements = sum(t[1] for t in reinforcement_tuples)
        card_sets = player.get_card_sets()
        player.remove_card_sets(card_sets)
        if total_reinforcements > reinforcement_count:
            raise ValueError("Reinforcement tuples exceed the allowed reinforcement count")


        for reinforcement_tuple in reinforcement_tuples:
            if reinforcement_tuple[1]>0:
                reinforcement_tuple[0].increment_troop_count(reinforcement_tuple[1])
            player.reset_player_units()

        return None
        
    def invade(self, player: Player) -> None:
        invading = True
        while invading:
            invasion = player.invade(self.get_adjacent_territories(player))
            if invasion is None:
                invading = False
            else:
                home_territory, target_territory, num_attacking_troops = invasion
                
                
                # Check if the target territory is owned by the player
                if target_territory.owner == player:
                    print(f"Cannot invade own territory: {target_territory.name}")
                    continue
                
                home_territory.decrement_troop_count(num_attacking_troops)
                
                success, num_remaining = target_territory.attack(num_attacking_troops)
                if success:
                    target_territory.owner.remove_player_territory(target_territory)
                    player.give_player_territory(target_territory, num_remaining)
                    target_territory.set_owner(player)
                    target_territory.set_troop_count(num_remaining)
                    if self.card_deck:
                        card = self.card_deck.pop()
                        player.add_card(card)
                    else:
                        self.card_deck = self.create_card_deck()
                    
                else:
                    pass

                
        return
        


    def get_adjacent_territories(self, player: Player) -> List[Tuple[Territory, List[Territory]]]:
        adjacent_territory_tuples = []

        for territory_id in player.personal_territories:
            adjacent_territories = []
            for adjacent_id in ADJACENCY_LIST.get(territory_id, []):
                adjacent_territory = self.territories[adjacent_id]
                if adjacent_territory.owner != player:
                    adjacent_territories.append(adjacent_territory)
            
            current_territory = self.territories[territory_id]
            adjacent_territory_tuples.append((current_territory, adjacent_territories))
        
        return adjacent_territory_tuples
    
    def manoeuvre(self, player: Player) -> None:
        manoveureable_territories = self.get_manoeuvreable_territories(player)
        
        source_territory, destination_territory, num_troops = player.manoeuvre(manoveureable_territories)
        if source_territory is None:
            return(None)
        source_territory.decrement_troop_count(num_troops)
        destination_territory.increment_troop_count(num_troops)
        
        return None

        
        
    def get_manoeuvreable_territories(self, player: Player) -> List[Tuple[Territory, List[Territory]]]:
        def bfs_reachable_territories(start_id: str, player_territories: set) -> List[Territory]:
            visited = set()
            queue = deque([start_id])
            reachable_territories = []

            while queue:
                current_id = queue.popleft()
                if current_id not in visited:
                    visited.add(current_id)
                    reachable_territories.append(self.territories[current_id])
                    for adjacent_id in ADJACENCY_LIST.get(current_id, []):
                        if adjacent_id in player_territories and adjacent_id not in visited:
                            queue.append(adjacent_id)

            return reachable_territories

        manoeuvreable_territory_tuples = []
        player_territories_set = set(player.personal_territories)

        for territory_id in player.personal_territories:
            reachable_territories = bfs_reachable_territories(territory_id, player_territories_set)
            reachable_territories.remove(self.territories[territory_id])  # Remove the start territory itself
            manoeuvreable_territory_tuples.append((self.territories[territory_id], reachable_territories))

        return manoeuvreable_territory_tuples

    
    
    


class Drawing():

    def __init__(self):
        pygame.init()
        self.font = pygame.font.Font(None, 20)
        self.window = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Risk Game UI")


    def draw_map(self,territories):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        self.window.fill(Colour.WHITE.value)

        self.draw_connections(territories)
        self.draw_territories(territories)
        mouse_pos = pygame.mouse.get_pos()
        hovered_territory = self.get_hovered_territory(mouse_pos)
        if hovered_territory:
           self.display_territory_info(hovered_territory, mouse_pos)

        

        pygame.display.flip()
    
    def draw_territories(self, territories : List[Territory]) -> None:
        for territory_id, territory in territories.items():
            position = territory.get_position()
            territory_size = 36
            pygame.draw.circle(self.window, territory.get_owner().get_colour() if territory.get_owner() else Colour.WHITE.value[0], position, territory_size)
            pygame.draw.circle(self.window, territory.get_outline_colour(), position, territory_size, 5)
            
            # Render the text and get its rectangle
            text = self.font.render(territory.name, True, Colour.BLACK.value)
            text_rect = text.get_rect(center=position)
            
            # Draw the text
            self.window.blit(text, text_rect)

    def draw_quadratic_bezier_curve(self, start_pos : Tuple[int], end_pos : Tuple[int], colour : Tuple[int], width=2, multiplier=1.5) -> None:
        points = []
        control_pos = ((start_pos[0] + end_pos[0]) // 2, start_pos[1] - int(100 * multiplier))
        for t in range(0, 101):
            t /= 100
            x = (1-t)**2 * start_pos[0] + 2*(1-t)*t * control_pos[0] + t**2 * end_pos[0]
            y = (1-t)**2 * start_pos[1] + 2*(1-t)*t * control_pos[1] + t**2 * end_pos[1]
            points.append((int(x), int(y)))
        pygame.draw.lines(self.window, colour, False, points, width)
        
        return None
    
    def draw_connections(self, territories : List[Territory]) -> None:
        for territory, neighbors in ADJACENCY_LIST.items():
            for neighbor in neighbors:
                if (territory, neighbor) == (30, 43) or (territory, neighbor) == (43, 30):
                    continue  # Skip the Kamchatka-Alaska connection for now
                start_pos = territories[territory].get_position()
                end_pos = territories[neighbor].get_position()
                pygame.draw.line(self.window, Colour.BLACK.value, start_pos, end_pos, 2)

        # Draw the curved connection between Kamchatka and Alaska
        kamchatka_pos = territories[30].get_position()
        alaska_pos = territories[43].get_position()
        self.draw_quadratic_bezier_curve(kamchatka_pos, alaska_pos, Colour.BLACK.value, 2, multiplier=y_height_multiplier)

        return None
    
    def get_hovered_territory(self, mouse_pos):
        for territory in territories.values():
            position = territory.get_position()
            territory_size = 36
            distance = ((mouse_pos[0] - position[0]) ** 2 + (mouse_pos[1] - position[1]) ** 2) ** 0.5
            if distance < territory_size:
                return territory
        return None
    
    def display_territory_info(self, territory, mouse_pos):
        info_text = f"Territory: {territory.name}\nOwner: {territory.get_owner().get_player_name() if territory.get_owner() else 'None'}\nTroop count: {territory.troop_count}"
        lines = info_text.split('\n')
        
        # Calculate the width and height of the text box
        text_width = max(self.font.size(line)[0] for line in lines) + 20
        text_height = self.font.get_height() * len(lines) + 20
        
        # Draw a white rectangle as the background for the text box
        pygame.draw.rect(self.window, Colour.WHITE.value[0], (mouse_pos[0] + 10, mouse_pos[1] + 10, text_width, text_height))
        pygame.draw.rect(self.window, Colour.BLACK.value[0], (mouse_pos[0] + 10, mouse_pos[1] + 10, text_width, text_height), 1)  # Border
        
        y_offset = 0
        for line in lines:
            info_surface = self.font.render(line, True, Colour.BLACK.value[0])
            self.window.blit(info_surface, (mouse_pos[0] + 20, mouse_pos[1] + 20 + y_offset))
            y_offset += self.font.get_height()




   















territories = {
    1: Territory("NWT",129*x_width_multiplier,79*y_height_multiplier, Continent.NORTH_AMERICA, 1 ),
    3: Territory("Greenland",266*x_width_multiplier,48*y_height_multiplier, Continent.NORTH_AMERICA, 3),
    4: Territory("Alberta", 110*x_width_multiplier, 125*y_height_multiplier, Continent.NORTH_AMERICA, 4),
    5: Territory("Ontario",172*x_width_multiplier,130*y_height_multiplier, Continent.NORTH_AMERICA, 5),
    6: Territory("Quebec", 230*x_width_multiplier, 133*y_height_multiplier, Continent.NORTH_AMERICA, 6),
    7: Territory("Western US", 112*x_width_multiplier, 183*y_height_multiplier, Continent.NORTH_AMERICA, 7),
    8: Territory("Eastern US",172*x_width_multiplier, 200*y_height_multiplier, Continent.NORTH_AMERICA, 8),
    9: Territory("Mexico", 121*x_width_multiplier, 257*y_height_multiplier, Continent.NORTH_AMERICA, 9),
    10: Territory("Venezuala", 177*x_width_multiplier, 301*y_height_multiplier, Continent.SOUTH_AMERICA, 10),
    11: Territory("Brazil", 235*x_width_multiplier, 359*y_height_multiplier, Continent.SOUTH_AMERICA, 11),
    12: Territory("Peru", 174*x_width_multiplier, 369*y_height_multiplier, Continent.SOUTH_AMERICA, 12),
    13: Territory("Argentina", 193*x_width_multiplier, 441*y_height_multiplier, Continent.SOUTH_AMERICA, 13),
    14: Territory("Iceland", 333*x_width_multiplier,100*y_height_multiplier, Continent.EUROPE, 14),
    15: Territory("Scandinavia",400*x_width_multiplier,94*y_height_multiplier, Continent.EUROPE, 15),
    16: Territory("GB",313*x_width_multiplier,165*y_height_multiplier, Continent.EUROPE, 16),
    17: Territory("North EU",388*x_width_multiplier,177*y_height_multiplier, Continent.EUROPE, 17),
    18: Territory("West EU", 337*x_width_multiplier, 238*y_height_multiplier, Continent.EUROPE, 18),
    19: Territory("South EU", 400*x_width_multiplier, 235*y_height_multiplier, Continent.EUROPE, 19),
    20: Territory("Ukraine",463*x_width_multiplier,145*y_height_multiplier, Continent.EUROPE, 20),
    21: Territory("North Africa", 356*x_width_multiplier, 340*y_height_multiplier, Continent.AFRICA, 21),
    22: Territory("Egypt", 421*x_width_multiplier, 311*y_height_multiplier, Continent.AFRICA, 22),
    23: Territory("East Africa", 472*x_width_multiplier, 378*y_height_multiplier, Continent.AFRICA, 23),
    24: Territory("Congo", 421*x_width_multiplier, 406*y_height_multiplier, Continent.AFRICA, 24),
    25: Territory("South Africa", 424*x_width_multiplier, 476*y_height_multiplier, Continent.AFRICA, 25),
    26: Territory("Madagascar", 503*x_width_multiplier, 479*y_height_multiplier, Continent.AFRICA, 26),
    27: Territory("Ural", 550*x_width_multiplier, 125*y_height_multiplier, Continent.ASIA, 27),
    28: Territory("Siberia", 593*x_width_multiplier, 80*y_height_multiplier, Continent.ASIA, 28),
    29: Territory("Yakutsk", 650*x_width_multiplier, 60*y_height_multiplier, Continent.ASIA, 29),
    30: Territory("Kamchatka",727*x_width_multiplier,60*y_height_multiplier, Continent.ASIA, 30),
    31: Territory("Kazakstan", 527*x_width_multiplier, 191*y_height_multiplier, Continent.ASIA, 31),
    32: Territory("Irkutsk",643*x_width_multiplier, 130*y_height_multiplier, Continent.ASIA, 32),
    33: Territory("Mongolia", 650*x_width_multiplier,182*y_height_multiplier, Continent.ASIA, 33),
    34: Territory("Japan",740*x_width_multiplier,183*y_height_multiplier, Continent.ASIA, 34),
    35: Territory("Middle East", 483*x_width_multiplier, 267*y_height_multiplier, Continent.ASIA, 35),
    36: Territory("India", 570*x_width_multiplier, 278*y_height_multiplier, Continent.ASIA, 36),
    37: Territory("China", 630*x_width_multiplier, 231*y_height_multiplier, Continent.ASIA, 37),
    38: Territory("Siam", 643*x_width_multiplier,298*y_height_multiplier, Continent.ASIA, 38),
    39: Territory("Indonesia",658*x_width_multiplier, 391*y_height_multiplier, Continent.AUSTRALIA, 39),
    40: Territory("New Guinea", 727*x_width_multiplier,370*y_height_multiplier, Continent.AUSTRALIA, 40),
    41: Territory("W Australia", 684*x_width_multiplier, 471*y_height_multiplier, Continent.AUSTRALIA, 41),
    42: Territory("E Australia", 756*x_width_multiplier, 459*y_height_multiplier, Continent.AUSTRALIA, 42),
    43: Territory("Alaska",44*x_width_multiplier,77*y_height_multiplier, Continent.NORTH_AMERICA, 43)
    }






player_count = 3

starting_infantry_dict = {
    2 : 40,
    3 : 35,
    4 : 30,
    5 : 25
}



players = []

for x in range(player_count):
    players.append(RandomAgent(x,starting_infantry_dict[player_count]))





game = Game(players, territories, simulating= True)
win_counts = {}
for player in game.stored_players:
    win_counts[player.id] = 0

results = []
for x in range(1, 20):
    winner_id = game.play_game(game.stored_players, max_turns= 200)
    
    print(f"Game {x}")
    if winner_id is not None:
        win_counts[winner_id] += 1


print("Win counts:")
for player in players:
    count = win_counts[player.id]
    print(f"{player.get_player_name()}: {count} wins")

    
    


pygame.quit()
sys.exit()