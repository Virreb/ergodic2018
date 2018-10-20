from api import API
import sys
from graph import create_baseline, visualize_path

_api_key = "c83a7b3d-0ca8-4060-9c5c-d7e5a3ae7297"
# Specify your API-key number of players per game),
# mapname, and number of waterstreams/elevations/powerups here
_api = API(_api_key, 1, "standardmap", 10, 10, 1)


# A "solution" that takes a step in a random direction every turn
def solution(game_id):
    initial_state = _api.get_game(game_id)
    if initial_state["success"]:
        state = initial_state["gameState"]
        tiles = state["tileInfo"]
        path, actions = create_baseline(tiles)
        visualize_path(tiles, path)
        exit()

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
