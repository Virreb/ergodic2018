
OPPOSITE_DIRS = {'w': 'e',
                 'e': 'w',
                 'n': 's',
                 's': 'n'}


def add_valid_edge(id_x, id_y, target_x, target_y, tiles):

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


def get_dir_from_tiles(from_tile, to_tile):

    diff_x = to_tile[1] - from_tile[1]
    diff_y = to_tile[0] - from_tile[0]

    if diff_x == 1:
        action = 'e'
    elif diff_x == -1:
        action = 'w'

    if diff_y == 1:
        action = 's'
    elif diff_y == -1:
        action = 'n'

    return action


def create_actions_from_path(path):

    actions = []
    for idx in range(0, len(path)-1):
        action = get_dir_from_tiles(from_tile=path[idx], to_tile=path[idx+1])
        actions.append(action)

    return actions


def create_baseline(tiles):
    import networkx as nx

    nbr_tiles = 100
    max_int = 100000
    move_cost = {'water': 45, 'road': 31, 'trail': 40, 'grass': 50, 'rain': 7, 'forest': max_int,
                 'start': max_int, 'win': 0}
    stamina_cost = {'fast': 50, 'medium': 30, 'slow': 10, 'step': 15}
    move_points = {'fast': 210, 'medium': 150, 'slow': 100}

    G = nx.DiGraph()

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

                if add_valid_edge(id_x, id_y, target_x, target_y, tiles) is True:

                    target_tile = tiles[target_y][target_x]
                    direction = get_dir_from_tiles((id_y, id_x), (target_y, target_x))

                    weight = move_cost[target_tile['type']]

                    if 'weather' in target_tile and target_tile['weather'] == 'rain':
                        weight += move_cost['rain']

                    if 'elevation' in target_tile:
                        elevation_dir = target_tile['elevation']['direction']
                        elevation_amount = target_tile['elevation']['amount']

                        if direction == elevation_dir:
                            weight -= elevation_amount
                        elif OPPOSITE_DIRS[direction] == elevation_dir:
                            weight += elevation_amount
                    elif 'waterstream' in target_tile:
                        waterstream_dir = target_tile['waterstream']['direction']
                        waterstream_speed = target_tile['waterstream']['speed']

                        if direction == waterstream_dir:
                            weight -= waterstream_speed
                        elif OPPOSITE_DIRS[direction] == waterstream_dir:
                            weight += waterstream_speed

                    G.add_edge((id_y, id_x), (target_y, target_x), weight=weight)

    #best_path = nx.astar_path(G, start, goal)
    best_path = nx.dijkstra_path(G, start, goal)
    actions = create_actions_from_path(best_path)

    return best_path, actions


def visualize_path(tiles, path):
    import numpy as np
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
        if tiles[tile[0]][tile[1]]['type'] == 'forest':
            plot_data[tile[0], tile[1]] = 5
            # print(f'x={tile[1]}, y={tile[0]}')

    fig, ax = plt.subplots()
    cmap = mpl.colors.ListedColormap(['g', 'b', 'black', 'y', 'r', 'c'])
    bounds = [0, 1, 2, 3, 4, 5, 6]
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
    ax.imshow(plot_data, cmap=cmap, norm=norm)
    plt.show()
