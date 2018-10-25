USE_INSTANT_POWERUPS = ['RestoreStamina', 'Energyboost', 'Potion', 'StaminaSale']
TILE_POWERUPS = {'water': ['Flippers'],
                 'trail': ['Shoes'],
                 'road': ['Cycletire'],
                 'rain': ['Umbrella', 'RemoveCloud']
                 }

NOT_PRIO_POWERUPS = ['Spikeshoes', 'BicycleHandlebar', 'Cyklop', 'Helmet', 'InvertStreams']


def check_for_applicable_powerups(powerup_inventory, active_powerups, counts):

    active_powerups_names = [d['name'] for d in active_powerups]
    powerups_to_activate = []

    for powerup in powerup_inventory:

        # NOT PRIO
        if len(powerup_inventory) == 3 and powerup in NOT_PRIO_POWERUPS:
            powerups_to_activate.append(powerup)

        # INSTANT POWERUPS
        if powerup in USE_INSTANT_POWERUPS:
            if powerup not in active_powerups_names:
                powerups_to_activate.append(powerup)

        # TILE POWERUPS
        for tile_type in ['water', 'trail', 'road']:
            if powerup in TILE_POWERUPS[tile_type]:
                if counts['next_all'][tile_type] == 0 and len(powerup_inventory) == 3 \
                        and counts['next_all']['win'] > 10:
                    powerups_to_activate.append(powerup)

                if counts['next_ten'][tile_type] > 4 and powerup not in active_powerups_names:
                    powerups_to_activate.append(powerup)

        # RAIN POWERUPS
        if powerup == 'RemoveCloud' and counts['next_one'] == 1:
            powerups_to_activate.append(powerup)

        if powerup == 'Umbrella' and 'RemoveCloud' not in powerups_to_activate \
                and (counts['next_ten']['rain'] > 4 or counts['next_one']['rain'] == 1):
            powerups_to_activate.append(powerup)

    return powerups_to_activate


