

from collections import defaultdict, deque
from enum import Enum
import time
import numpy as np
import pygame
import sys
from typing import List, Dict, Tuple
import random


from Agent import RandomAgent, Player
from AggressiveAgent import AggressiveAgent



class Continent(Enum):
    NORTH_AMERICA = 1
    SOUTH_AMERICA = 2
    EUROPE = 3
    AFRICA = 4
    ASIA = 5
    AUSTRALIA = 6


class Stage(Enum):
    SELECTION = 1,
    PLACEMENT = 2,


class Colour(Enum):
    SEA = (0, 255, 255),
    WHITE = (255, 255, 255),
    BLACK = (0, 0, 0),
    RED = (200, 0, 0),
    BLUE = (0, 0, 255),
    GREEN = (0, 255, 0),
    RUST = (210, 150, 75),
    LIME = (180, 255, 100)

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






    
    

class Territory():
    def __init__(self, name: str, x_pos: int, y_pos: int, continent: Continent, id: int):
        self.name = name
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.continent = continent
        self.owner = None
        self.troop_count = 0
        self.id = id
        self.reachable_territories = set()
        

    # def get_adjacent(self) -> List['Territory']:
    #     returned_territories = []
    #     for territory_id in ADJACENCY_LIST[self.id]:
    #         pass
            



    def get_position(self) -> tuple:
        return ((self.x_pos, self.y_pos))

    def get_owner(self) -> Player:
        return (self.owner)

    def set_owner(self, owner: Player) -> None:
        self.owner = owner
        return None

    def get_troop_count(self) -> int:
        return (self.troop_count)

    def set_troop_count(self, troop_count: int) -> None:
        self.troop_count = troop_count
        return None

    def increment_troop_count(self, troop_increment: int) -> None:
        if troop_increment > 0:
            self.troop_count += troop_increment
            return None
        else:
            raise ArithmeticError()

    def decrement_troop_count(self, troop_decrement: int) -> None:
        if troop_decrement > 0:
            self.troop_count -= troop_decrement
            return None
        else:
            raise ArithmeticError()

    def reset(self) -> None:
        self.owner = None
        self.troop_count = 0

        return None

    def attack(self, attacking_troops: int):
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
            Continent.NORTH_AMERICA: (255, 255, 0),  # Yellow
            Continent.SOUTH_AMERICA: (255, 100, 10),  # Orange
            Continent.EUROPE: (0, 0, 100),  # Blue
            Continent.AFRICA: (205, 245, 255),  # White
            Continent.ASIA: (0, 255, 0),  # Green
            Continent.AUSTRALIA: (240, 0, 255)  # Purple
        }
        return (continent_colour_dict[self.continent])


class Game():
    def __init__(self, players : List[Player], territories : Dict[Territory, int], simulating : bool  = False, num_players = 3):
        if not simulating:
            self.drawing = Drawing()
        random.shuffle(players) # random.shuffle shuffles in-place.
        self.turn_order = players

        
        self.simulating = simulating
        self.territories = territories
        self.stored_players = players
        if players == []:
            self.num_players = num_players
        else:
            self.num_players = len(players)

        self.precomputed_adjacent_territories = {}
        for territory_id, territory in self.territories.items():
            adjacent_ids = ADJACENCY_ARRAY[territory_id]
            adjacent_territories = [self.territories[adjacent_id] for adjacent_id in adjacent_ids]
            self.precomputed_adjacent_territories[territory_id] = adjacent_territories
        # self.start_turns(players)

    
    def reset_game(self):
        for territory in self.territories.values():
            territory.reset()

        for player in self.stored_players:
            player.reset()
        random.shuffle(self.stored_players)

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
                    if not self.simulating:
                        time.sleep(0.1)
        
            # Update the list of players with active players
            players = active_players

            # arr = [(x, 0) for x in range(0,len(ADJACENCY_ARRAY))]
            # print(arr)

            # Check if there is only one player remaining or the maximum number of turns is reached
            if len(players) == 1 or turn_count >= max_turns:
                running = False

                # Count the number of territories each player has
                player_territory_count = {}
                for player in players:
                    player_territory_count[player.id] = len(player.personal_territories)

                # Find the player with the most territories
                
                max_territories_player = max(player_territory_count, key=player_territory_count.get)
                fitnesses = self.get_fitness(max_territories_player)
                return max_territories_player, fitnesses
            if not self.simulating:
                self.drawing.draw_map(self.territories)

            turn_count += 1
            # input()

        return None
    
    def get_fitness(self, best_player : Player) -> List[int]:
        fitness_scores = []
        for player in self.stored_players:

            no_territories = len(list(player.personal_territories))
            no_troops_per_turn = player.base_reinforcement
            win = 20 if player.id == best_player else 0
            fitness_score = no_territories + no_troops_per_turn + win
            fitness_scores.append(fitness_score)
        return(fitness_scores)


        

    def selection(self, players: List[Player]) -> List[Player]:  # I'm going to make this return the state of turns when it's done selection
        for x in range(len(territories.items())):
            current_player = players.pop(0)
            players.append(current_player)  # Circular 

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

        return (available_territories)

    def add_infantry(self, players: List[Player]) -> List[Player]:
        iterations = players[0].unassigned_units * len(players)
        for x in range(iterations):

            current_player = players.pop(0)
            players.append(current_player)  # Circular 

            selected_territory = current_player.add_infantry()
            selected_territory.increment_troop_count(1)
            current_player.remove_player_units(1)
        return players

    def main_section(self, player: Player) -> None:
        personal_territories_changed = player.personal_territories_changed()
        self.reinforce(player, personal_territories_changed = personal_territories_changed)
        self.invade(player, personal_territories_changed = personal_territories_changed)
        self.manoeuvre(player, personal_territories_changed = personal_territories_changed)
        

    def reinforce(self, player: Player, personal_territories_changed : bool = False) -> None:
        reinforcement_count = player.calculate_reinforcement(personal_territories_changed)

        player.give_player_units(reinforcement_count)
        reinforcement_tuples = player.reinforce(reinforcement_count)

        # Verify that the total number of reinforcements does not exceed the allowed reinforcement count
        total_reinforcements = sum(t[1] for t in reinforcement_tuples)
        
        if total_reinforcements > reinforcement_count:
            raise ValueError("Reinforcement tuples exceed the allowed reinforcement count")

        for reinforcement_tuple in reinforcement_tuples:
            if reinforcement_tuple[1] > 0:
                reinforcement_tuple[0].increment_troop_count(reinforcement_tuple[1])
            player.reset_player_units()

        return None
        
    def invade(self, player: Player, personal_territories_changed: bool = False) -> bool:
        invading = True
        successfully_attacked = False
        while invading:
            invasion = player.invade(self.get_enemy_adjacent_territories(player, changed = personal_territories_changed))
            if invasion is None:
                invading = False
                if successfully_attacked:
                    player.add_card()
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
                    successfully_attacked = True
                    
                        
                    # player.add_card(card)
                    
                    
                else:
                    pass

                
        return successfully_attacked
        


    def get_enemy_adjacent_territories(self, player: Player,changed : bool) -> List[Tuple[Territory, List[Territory]]]:
        if changed:
            player_territories_set = set(player.personal_territories)
            enemy_adjacent_territories = []

            for territory_id in player.personal_territories:
                adjacent_territories = self.precomputed_adjacent_territories[territory_id]
                adjacent_enemy_territories = [t for t in adjacent_territories if t.id not in player_territories_set]
                enemy_adjacent_territories.append((self.territories[territory_id], adjacent_enemy_territories))

            player.adjacent_territories_cache = enemy_adjacent_territories

        return player.adjacent_territories_cache
    
    def manoeuvre(self, player: Player, personal_territories_changed: bool = True) -> None:
        
        manoveureable_territories = self.get_manoeuvreable_territories(player, changed = personal_territories_changed)
        
        source_territory, destination_territory, num_troops = player.manoeuvre(manoveureable_territories)
        
        if source_territory is None:
            return None 
        
        if source_territory.get_troop_count()<num_troops:
            if source_territory.get_troop_count()>1:
                source_territory.decrement_troop_count(1) # Bad programming punishment.
            return None
        
        source_territory.decrement_troop_count(num_troops)
        destination_territory.increment_troop_count(num_troops)

        return None
    
    def get_manoeuvreable_territories(self, player: Player, changed: bool = True) -> List[Tuple[Territory, List[Territory]]]:
        if changed:
            player_territories_set = set(player.personal_territories)
            maneuverable_territories = []

            # Create an adjacency list representation of the graph
            adjacency_list = defaultdict(list)
            for territory_id in player_territories_set:
                adjacent_ids = ADJACENCY_ARRAY[territory_id]
                for adjacent_id in adjacent_ids:
                    if adjacent_id in player_territories_set:
                        adjacency_list[territory_id].append(adjacent_id)

            # Perform DFS to find connected components (islands)
            visited = set()
            island_map = {}
            island_territories = defaultdict(set)

            def dfs(territory_id, island_num):
                visited.add(territory_id)
                island_map[territory_id] = island_num
                island_territories[island_num].add(territory_id)
                for adjacent_id in adjacency_list[territory_id]:
                    if adjacent_id not in visited:
                        dfs(adjacent_id, island_num)

            island_num = 0
            for territory_id in player_territories_set:
                if territory_id not in visited:
                    island_num += 1
                    dfs(territory_id, island_num)

            # Create maneuverable territories using the island information
            for territory_id in player_territories_set:
                island_num = island_map[territory_id]
                reachable_territories = [self.territories[t_id] for t_id in island_territories[island_num] if t_id != territory_id]
                maneuverable_territories.append((self.territories[territory_id], reachable_territories))

            player.manoeuvreable_tiles = maneuverable_territories
            return maneuverable_territories
        else:
            return player.manoeuvreable_tiles
    

class Drawing():

    def __init__(self):
        pygame.init()
        self.territories = []
        self.font = pygame.font.Font(None, 20)
        self.window = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Risk Game UI")


    def draw_map(self,territories):
        
        for event in pygame.event.get():
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self.handle_mouse_click(mouse_pos, game)
                clicked = True

                
        self.window.fill(Colour.WHITE.value)

        self.draw_connections(territories)
        self.draw_territories(territories)
        mouse_pos = pygame.mouse.get_pos()
        hovered_territory = self.get_hovered_territory(mouse_pos)
        if hovered_territory:
           self.display_territory_info(hovered_territory, mouse_pos)
        self.highlight_territories()
        

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
    
    def draw_connections(self, territories: Dict[int, Territory]) -> None:
        for territory_id, territory in territories.items():
            if territory_id == 0:
                continue  # Skip territory ID 0 since it's not used
            for neighbor_id in ADJACENCY_ARRAY[territory_id]:
                if (territory_id, neighbor_id) == (30, 43) or (territory_id, neighbor_id) == (43, 30):
                    continue  # Skip the Kamchatka-Alaska connection for now
                start_pos = territory.get_position()
                end_pos = territories[neighbor_id].get_position()
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

    def handle_mouse_click(self, mouse_pos, game):
        clicked_territory = self.get_hovered_territory(mouse_pos)
        if clicked_territory:
            player = clicked_territory.get_owner()
            if player:
                manoeuvreable_tiles = game.get_manoeuvreable_territories(player)
               
                for source_territory, dest_territories in manoeuvreable_tiles:
                    print(clicked_territory.name)
                    print(source_territory.name)
                    if clicked_territory == source_territory:
                       
                        #self.highlight_territories(dest_territories)
                        self.territories = dest_territories
                        break

    def highlight_territories(self):
        #print("Highlighting territories:")
        for territory in self.territories:
            #print(territory.name)
            position = territory.get_position()
            territory_size = 40
            pygame.draw.circle(self.window, Colour.LIME.value, position, territory_size, 5)


class GeneticAlgorithm():
    
        
    def __init__(self, num_generations : int, population_size : int, game : Game) -> None:
        self.num_generations = num_generations
        self.population_size = population_size
        self.game = game
        
        

    def initialize_population(self):

        #self.attack_heuristic_weightings = {
        #     1: 1, # Point of interest
        #     2: 1, # If the territory is able to attack and gain the entire continent.
        #     3: 1, # If it places you below max troops
        #     4: 1, # Gives increased reinforcements  ( increasing from 13 territories to 14)
        #     5: 1, # If you're able to find a chain of attacks
        #     6: 1, # If the territory attack is able to decrease the number of borders.
        #     7: 1, # If the opponent is winning
        #     8: 1, # Troop differential
        #     9: 1, # If it exposes you to chaining
        #     10: 7, # Heuristic threshold
            
            
        # }
        
        population = []
        for _ in range(self.population_size):
            weightings  = [random.random() for _ in range(10)]
            player = AggressiveAgent(0, starting_infantry_dict[self.game.num_players], weightings)  # Assuming RandomAgent is used for all players
            population.append(player)
        return population
    
    def evolve(self):
        population = self.initialize_population()
        for generation in range(self.num_generations):
            print(f"Generation {generation + 1}")

            fitness_scores = self.evaluate_fitness(self.game, population)
            print(fitness_scores)




    
    def evaluate_fitness(self, game, population):
        fitness_scores = []
        start_time = time.time()
        num_games = 10

        for individual in population:
            total_fitness = 0

            for _ in range(num_games):
                # Create a new list of players for each game
                players = [individual]
                
                # Add random players to the game
                for _ in range(game.num_players-1):
                    random_player = random.choice(population)
                    players.append(random_player)
                game.stored_players = players

                
                

                # Play the game and get the fitness score
                winner_id, fitness = game.play_game(players, max_turns=200)
                total_fitness += fitness[0]  # Assuming we only care about the first player's fitness

            # Calculate the average fitness score over the 10 games
            average_fitness = total_fitness / num_games
            fitness_scores.append(average_fitness)
        print(time.time()-start_time)
        return fitness_scores
    




   















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
    2: 40,
    3: 35,
    4: 30,
    5: 25
}


players = []

players.append(RandomAgent(0, starting_infantry_dict[player_count]))

for x in range(1, player_count):
    players.append(RandomAgent(x, starting_infantry_dict[player_count]))









game = Game(players, territories,  simulating = True)
win_counts = {}
for player in game.stored_players:
    win_counts[player.id] = 0

genetic_algo = GeneticAlgorithm(30, 30, game)
genetic_algo.evolve()

results = []

for x in range(1, 2000):
    winner_id, fitness = game.play_game(game.stored_players, max_turns= 200)
    
    print(f"Game {x}")
    if winner_id is not None:
        win_counts[winner_id] += 1


print("Win counts:")
for player in players:
    count = win_counts[player.id]
    print(f"{player.get_player_name()}: {count} wins")

    
    

if not game.simulating:
    pygame.quit()
sys.exit()
