from api import API
import random
import sys
from test import aStar
import numpy as np

_api_key = "c83a7b3d-0ca8-4060-9c5c-d7e5a3ae7297"
# Specify your API-key number of players per game),
# mapname, and number of waterstreams/elevations/powerups here
_api = API(_api_key, 1, "standardmap", 10, 10, 10)


def visualize_solution(tiles, path):
    import matplotlib.pyplot as plt
    import matplotlib as mpl
    nbr_tiles = len(tiles)

    plot_data = np.zeros(shape=(nbr_tiles, nbr_tiles))

    for idy in range(0, nbr_tiles):
        for idx in range(0, nbr_tiles):
            tile_type = tiles[idy][idx]['type']

            if tile_type == 'grass':
                plot_data[idy, idx] = 0
            elif tile_type == 'water':
                plot_data[idy, idx] = 1
            elif tile_type == 'road':
                plot_data[idy, idx] = 2
            elif tile_type == 'trail':
                plot_data[idy, idx] = 3

    for tile in path:
        plot_data[tile[0], tile[1]] = 4

        if tiles[tile[0]][tile[1]] == 'forest':
            plot_data[tile[0], tile[1]] = 5
        # print(f'x={tile[1]}, y={tile[0]}')

    fig, ax = plt.subplots()
    cmap = mpl.colors.ListedColormap(['g', 'b', 'b', 'y', 'r', 'c'])
    bounds = [0, 1, 2, 3, 4, 5, 6]
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
    ax.imshow(plot_data, cmap=cmap, norm=norm)
    plt.show()


# A "solution" that takes a step in a random direction every turn
def solution(game_id):
    initial_state = _api.get_game(game_id)
    if initial_state["success"]:
        state = initial_state["gameState"]
        tiles = state["tileInfo"]
        current_player = state["yourPlayer"]
        current_y_pos = current_player["yPos"]
        current_x_pos = current_player["xPos"]

        path, actions = aStar(tiles)
        visualize_solution(tiles, path)

        idx = 0
        while not state["gameStatus"] == "done":
        #for action in actions:
            # print("Starting turn: " + str(state["turn"]))

            action = actions[idx]

            print(f'\\x={state["yourPlayer"]["xPos"]}, y={state["yourPlayer"]["yPos"]}, action={action}, '
                  f'state={state["yourPlayer"]["status"]}')

            response = _api.step(game_id, action)
            state = response["gameState"]

            if state['yourPlayer']['status'] == 'idle':
                print(f'STUNNED')
            else:
                idx += 1

        print("Finished!")
    else:
        print(initial_state["message"])


def main():
    game_id = "8366ab02-6d42-48c7-bf7c-d7b205968dd6"
    # If no gameID is specified as parameter to the script,
    # Initiate a game with 1 player on the standard map
    if len(sys.argv) == 1:
        _api.end_previous_games_if_any()  # Can only have 2 active games at once. This will end any previous ones.
        game_id = _api.init_game()
        joined_game = _api.join_game(game_id)
        readied_game = _api.try_ready_for_game(game_id)
        if readied_game is not None:
            print("Joined and readied! Solving...")
            solution(game_id)
    else:
        game_id = sys.argv[1]


main()
