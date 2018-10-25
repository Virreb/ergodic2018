
OPPOSITE_DIRS = {'w': 'e',
                 'e': 'w',
                 'n': 's',
                 's': 'n'}

DIR_OFFSET = {'n': (-1, 0),
              's': (1, 0),
              'w': (0, -1),
              'e': (0, 1)}

NBR_TILES = 100
MAX_INT = 100000
RAIN_PUNISHMENT = 10    # TODO: Optimize, not used?
STAMINA_SAFETY = 1

MOVEMENT_COST = {'water': 45, 'road': 31, 'trail': 40, 'grass': 50, 'rain': RAIN_PUNISHMENT, 'forest': MAX_INT,
                 'start': 30, 'win': 30}    # TODO: changed from max_int to 30 and 0 to 30
STAMINA_COST = {'fast': 50, 'medium': 30, 'slow': 10, 'step': 15}
MOVEMENT_POINTS = {'fast': 210, 'medium': 150, 'slow': 100}


def add_valid_edge(id_x, id_y, target_x, target_y, tiles):

    if id_x == 0 and target_x == -1:
        return False

    elif id_x == 99 and target_x == 100:
        return False

    if id_y == 0 and target_y == -1:
        return False

    elif id_y == 99 and target_y == 100:
        return False

    if tiles[target_y][target_x]['type'] in ['forest', 'rockywater']:  # Todo: Check rocky water
        return False

    if tiles[id_y][id_x]['type'] in ['forest', 'rockywater']:  # Todo: Check rocky water
        return False

    return True


def get_dir_from_tiles(from_tile, to_tile):

    diff_x = to_tile[1] - from_tile[1]
    diff_y = to_tile[0] - from_tile[0]

    if diff_x > 0:
        action = 'e'
    elif diff_x < 0:
        action = 'w'

    if diff_y > 0:
        action = 's'
    elif diff_y < 0:
        action = 'n'

    return action


def create_actions_from_path(path):

    actions = []
    for idx in range(0, len(path)-1):
        action = get_dir_from_tiles(from_tile=path[idx], to_tile=path[idx+1])
        actions.append(action)

    return actions


def check_special_movements(tiles, cost_graph, current_pos, current_stamina, direction, speed, active_powerups):
    applicable_movement = True
    total_movement_cost = 0

    potion_active = 'Potion' in active_powerups

    updated_stamina = current_stamina - STAMINA_COST[speed]
    if updated_stamina < STAMINA_SAFETY and speed in ['medium', 'fast']:
        return False, None, None, None

    iteration_current_pos = current_pos
    counter = 0
    while True:
        target_pos = (iteration_current_pos[0] + DIR_OFFSET[direction][0], iteration_current_pos[1] + DIR_OFFSET[direction][1])

        if add_valid_edge(iteration_current_pos[1], iteration_current_pos[0], target_pos[1], target_pos[0], tiles):
            target_tile_cost = cost_graph[iteration_current_pos][target_pos]['weight']
            total_movement_cost += target_tile_cost

            if 'weather' in tiles[target_pos[0]][target_pos[1]]:
                updated_stamina -= 7

                if updated_stamina < STAMINA_SAFETY and speed in ['medium', 'fast']:
                    return False, None, None, None

            counter += 1

            if total_movement_cost > (MOVEMENT_POINTS[speed] * (1 + 0.5*wq)):
                break

            iteration_current_pos = target_pos

        else:
            applicable_movement = False
            break

    if applicable_movement:
        total_movement_cost = total_movement_cost/counter

    return applicable_movement, total_movement_cost, updated_stamina, target_pos


def create_baseline(tiles, current_pos, current_stamina, active_powerups):
    import networkx as nx

    cost_graph = nx.DiGraph()
    optimize_graph = nx.DiGraph()

    for id_y in range(0, NBR_TILES):
        for id_x in range(0, NBR_TILES):
            current_tile = tiles[id_y][id_x]
            if current_tile['type'] == 'win':
                goal = (id_y, id_x)
            # elif tiles[id_y][id_x]['type'] == 'start':
            #     start = (id_y, id_x)

            for y, x in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                target_x = id_x + x
                target_y = id_y + y

                if add_valid_edge(id_x, id_y, target_x, target_y, tiles) is True:

                    target_tile = tiles[target_y][target_x]
                    direction = get_dir_from_tiles((id_y, id_x), (target_y, target_x))

                    # adjust weights
                    weight_reduction = 1
                    if target_tile['type'] == 'road' and 'Cycletire' in active_powerups:
                        weight_reduction *= 0.75
                    elif target_tile['type'] == 'water' and 'Flippers' in active_powerups:
                        weight_reduction *= 0.75
                    elif target_tile['type'] == 'trail' and 'Shoes' in active_powerups:
                        weight_reduction *= 0.75

                    weight = weight_reduction * MOVEMENT_COST[target_tile['type']]
                    # weight = MOVEMENT_COST[target_tile['type']]

                    # if 'weather' in target_tile and target_tile['weather'] == 'rain':
                    #     weight += MOVEMENT_COST['rain']

                    if 'elevation' in target_tile and 'Spikeshoes' not in active_powerups:
                        elevation_dir = target_tile['elevation']['direction']
                        elevation_amount = target_tile['elevation']['amount']

                        if direction == elevation_dir:
                            weight -= elevation_amount
                        elif OPPOSITE_DIRS[direction] == elevation_dir:
                            weight += elevation_amount
                    elif 'waterstream' in target_tile and 'Cyklop' not in active_powerups:
                        waterstream_dir = target_tile['waterstream']['direction']
                        waterstream_speed = target_tile['waterstream']['speed']

                        if direction == waterstream_dir:
                            weight -= waterstream_speed
                        elif OPPOSITE_DIRS[direction] == waterstream_dir:
                            weight += waterstream_speed

                    cost_graph.add_edge((id_y, id_x), (target_y, target_x), weight=weight)
                    optimize_graph.add_edge((id_y, id_x), (target_y, target_x), weight=1)

    movement = {}
    for speed in ['fast', 'medium', 'slow']:
        for direction in ['n', 'e', 's', 'w']:

            applicable_movement, total_movement_cost, updated_stamina, target_pos = \
                check_special_movements(tiles, cost_graph, current_pos, current_stamina,
                                        direction, speed, active_powerups)

            if applicable_movement:

                cost_graph.add_edge(current_pos, target_pos, weight=total_movement_cost)
                optimize_graph.add_edge(current_pos, target_pos, weight=1)
                movement[target_pos] = {'speed': speed, 'direction': direction}

                if updated_stamina < 65:
                    updated_stamina += 15
                else:
                    updated_stamina += 20

                create_special_movement_connections(tiles, cost_graph, optimize_graph, current_pos, current_stamina,
                                                    active_powerups, max_depth=1)

    #best_path = nx.astar_path(G, start, goal)
    #best_path = nx.dijkstra_path(cost_graph, current_pos, goal)
    best_path = nx.dijkstra_path(optimize_graph, current_pos, goal)
    #  try:
    #      visualize_path(tiles, best_path)
    #  except:
    #      pass

    # print(best_path[0], best_path[1])

    return best_path, movement


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
        if tiles[tile[0]][tile[1]]['type'] in ['forest', 'rocky_water']:
            plot_data[tile[0], tile[1]] = 5
            # print(f'x={tile[1]}, y={tile[0]}')

    fig, ax = plt.subplots()
    cmap = mpl.colors.ListedColormap(['g', 'b', 'black', 'y', 'r', 'c'])
    bounds = [0, 1, 2, 3, 4, 5, 6]
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
    ax.imshow(plot_data, cmap=cmap, norm=norm)
    #plt.show()
    plt.savefig('tmp.png')


def get_path_counts(tiles, path):

    init = {'water': 0, 'trail': 0, 'road': 0, 'win': 0, 'start': 0, 'rain': 0, 'grass': 0}
    counts = {'next_all': init.copy(), 'next_ten': init.copy(), 'next_one': init.copy(), 'to': init.copy()}

    for idx, pos in enumerate(path):
        y, x = pos[0], pos[1]
        tile_type = tiles[y][x]['type']

        is_rain = 'weather' in tiles[y][x] and tiles[y][x]['weather'] == 'rain'

        if is_rain and counts['to']['rain'] == 0:
            counts['to']['rain'] = idx

        if idx == 0:
            current_type = tile_type
        else:
            counts['next_all'][tile_type] += 1

            if idx == 1:
                counts['next_one'][tile_type] += 1

                if is_rain and counts['next_one']['rain'] == 0:
                    counts['next_one']['rain'] += 1

            if idx <= 10:
                counts['next_ten'][tile_type] += 1

                if is_rain and counts['next_ten']['rain'] == 0:
                    counts['next_ten']['rain'] = idx

            if current_type != tile_type and counts['to'][tile_type] == 0:
                counts['to'][tile_type] = idx

    return counts


def get_next_action_from_path(path, movement, counts, current_stamina):

    step_direction = get_dir_from_tiles(path[0], path[1])
    is_rain = counts['next_one']['rain']

    if path[1] in movement:
        if current_stamina - (10 + 7*is_rain) < 0:
            return {'speed': 'rest'}
        else:
            return movement[path[1]]
    else:
        if current_stamina - (15 + 7 * is_rain) < 0:
            return {'speed': 'rest'}
        else:
            return {'speed': 'step', 'direction': step_direction}


def create_special_movement_connections(tiles, cost_graph, optimize_graph, current_pos,
                                        current_stamina, active_powerups, max_depth=4):

    for speed in ['fast', 'medium', 'slow']:
        for direction in ['n', 'e', 's', 'w']:

            applicable_movement, total_movement_cost, updated_stamina, target_pos = \
                check_special_movements(tiles, cost_graph, current_pos, current_stamina,
                                        direction, speed, active_powerups)

            if applicable_movement:
                cost_graph.add_edge(current_pos, target_pos, weight=total_movement_cost)
                optimize_graph.add_edge(current_pos, target_pos, weight=1)

                if updated_stamina < 65:
                    updated_stamina += 15*0.7
                else:
                    updated_stamina += 20*0.7   # TODO: CHECK THIS SCIENTIFIC LIMIT

                if max_depth > 0:
                    create_special_movement_connections(tiles, cost_graph, optimize_graph, target_pos, updated_stamina,
                                                        active_powerups, max_depth-1)
