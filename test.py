import numpy as np
from api import API
import random
import sys
import networkx as nx
import matplotlib.pyplot as plt

# _api_key = "c83a7b3d-0ca8-4060-9c5c-d7e5a3ae7297"
# _api = API(_api_key, 1, "standardmap", 10, 10, 10)
#
# # _api.end_previous_games_if_any()  # Can only have 2 active games at once. This will end any previous ones.
# game_id = "879fef72-a669-43d1-a00f-b584df36b047"
# # game_id = _api.init_game()
# # joined_game = _api.join_game(game_id)
# # readied_game = _api.try_ready_for_game(game_id)
#
# initial_state = _api.get_game(game_id)
# print(initial_state)
# state = initial_state["gameState"]
# tiles = state["tileInfo"]
#current_player = state["yourPlayer"]
#current_y_pos = current_player["yPos"]
#current_x_pos = current_player["xPos"]


def aStar(tiles):
    nbr_tiles = 100
    max_int = 100000
    move_cost = {'water': 45, 'road': 31, 'trail': 40, 'grass': 50, 'rain': 7, 'forest': max_int,
                 'start': max_int, 'win': 0}
    stamina_cost = {'fast': 50, 'medium': 30, 'slow': 10, 'step': 15}
    move_points = {'fast': 210, 'medium': 150, 'slow': 100}

    # tiles = np.array(tiles)
    G = nx.Graph()

    def add_edge(id_x, id_y, target_x, target_y):

        if id_x == 0 and target_x == -1:
            return False

        elif id_x == 99 and target_x == 100:
            return False

        if id_y == 0 and target_y == -1:
            return False

        elif id_y == 99 and target_y == 100:
            return False

        if tiles[target_y][target_x]['type'] == 'forest':  # Todo: Check rocky water
            return False

        if tiles[id_y][id_x]['type'] == 'forest':  # Todo: Check rocky water
            return False

        return True
    nbr_forests_in_g = 0
    for id_y in range(0, nbr_tiles):
        for id_x in range(0, nbr_tiles):

            if tiles[id_y][id_x]['type'] == 'win':
                goal = (id_y, id_x)
            elif tiles[id_y][id_x]['type'] == 'start':
                start = (id_y, id_x)

            # TODO: Also check for streams and elevation

            for y, x in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                target_x = id_x + x
                target_y = id_y + y

                if add_edge(id_x, id_y, target_x, target_y) is True:
                    G.add_edge((id_y, id_x), (target_y, target_x), weight=move_cost[tiles[target_y][target_x]['type']])

                    if tiles[target_y][target_x]['type'] == 'forest':
                        nbr_forests_in_g += 1

    print('Number of forests in G:' + str(nbr_forests_in_g))
    nodes = G.nodes
    if (73, 13) in nodes:
        print(tiles[73][13])
        print('!!!')
        exit()
    best_path = nx.astar_path(G, start, goal)

    actions = []
    for idx in range(0, len(best_path)-1):
        diff_x = best_path[idx+1][1] - best_path[idx][1]
        diff_y = best_path[idx+1][0] - best_path[idx][0]

        if diff_x == 1:
            action = 'e'
        elif diff_x == -1:
            action = 'w'

        if diff_y == 1:
            action = 's'
        elif diff_y == -1:
            action = 'n'

        actions.append(action)

    return best_path, actions
