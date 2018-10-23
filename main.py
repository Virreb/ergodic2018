from api import API
import sys
from graph import create_baseline, visualize_path, get_path_counts, get_next_action_from_path
import time

_api_key = "c83a7b3d-0ca8-4060-9c5c-d7e5a3ae7297"
# Specify your API-key number of players per game),
# mapname, and number of waterstreams/elevations/powerups here
_api = API(_api_key, 1, "standardmap", 10, 10, 1)


# A "solution" that takes a step in a random direction every turn
def solve(game_id):
    initial_state = _api.get_game(game_id)
    if initial_state["success"]:
        state = initial_state["gameState"]
        print('Solving')

        # while not current_tile_type == 'win':
        while not state["gameStatus"] == "done":

            start_time = time.time()
            tiles = state["tileInfo"]
            current_pos = (state['yourPlayer']['yPos'], state['yourPlayer']['xPos'])
            current_stamina = state['yourPlayer']['stamina']

            best_path, movement = create_baseline(tiles, current_pos, current_stamina)
            counts = get_path_counts(tiles, best_path)
            next_action = get_next_action_from_path(best_path, movement, counts, current_stamina)

            if next_action['speed'] == 'rest':
                response = -_api.rest(game_id)
            elif next_action['speed'] == 'step':
                response = _api.step(game_id, next_action['direction'])
            else:
                response = _api.make_move(game_id, next_action['direction'], next_action['speed'])

            state = response["gameState"]

            # debug
            current_pos = (state['yourPlayer']['yPos'], state['yourPlayer']['xPos'])
            current_tile_type = tiles[current_pos[0]][current_pos[1]]['type']
            if state['yourPlayer']['status'] in ['idle', 'exhausted', 'stunned']:
                print(f'FUCK!!!!!')
                print(f'x={state["yourPlayer"]["xPos"]}, y={state["yourPlayer"]["yPos"]}, '
                      f'state={state["yourPlayer"]["status"]}, stamina={state["yourPlayer"]["stamina"]}, '
                      f'current tile={current_tile_type}')
                print('  ')
                #visualize_path(tiles, best_path)
                break

            # print(f'time for iteration: {time.time() - start_time}')

        print(f'Finished! in {state["gameState"]["turn"]} turns')
    else:
        print(initial_state["message"])


def join_game(game_id=None, end_previous_game=True):

    if end_previous_game is True:
        _api.end_previous_games_if_any()  # Can only have 2 active games at once. This will end any previous ones.

    if game_id is None:
        game_id = _api.init_game()

    _api.join_game(game_id)

    return game_id


def ready_game(game_id=None, end_previous_game=True):

    if game_id is None:
        game_id = join_game(end_previous_game=end_previous_game)

    readied_game_id = _api.try_ready_for_game(game_id)

    if readied_game_id is not None:
        print(f'Debug: http://www.theconsidition.se/ironmandebugvisualizer?gameId={game_id}')
        print(f'Visualizer: http://www.theconsidition.se/ironmanvisualizer?gameId={game_id}')
        solve(game_id)
    else:
        print(f'Could not ready up for {game_id}')


current_game_id = None
# game_id = ''
current_game_id = join_game(current_game_id, end_previous_game=True)
ready_game(current_game_id)

