USE_INSTANT_POWERUPS = ['RestoreStamina', 'InvertStreams', 'Energyboost', 'Potion', 'Helmet', 'StaminaSale']
TILE_POWERUPS = {'water': ['Flippers', 'Cyklop'],
                 'trail': ['Shoes', 'Spikeshoes'],
                 'road': ['Cycletire', 'BicycleDandlebar'],
                 'rain': ['Umbrella', 'RemoveCloud']
                 }


def check_for_applicable_powerups(powerup_inventory, active_powerups, counts):

    active_powerups_names = [d['name'] for d in active_powerups]
    powerups_to_activate, powerups_to_drop = [], []

    for powerup in powerup_inventory:

        # INSTANT POWERUPS
        if powerup in USE_INSTANT_POWERUPS:
            if powerup not in active_powerups_names:
                powerups_to_activate.append(powerup)

        # TILE POWERUPS
        for tile_type in ['water', 'trail', 'road']:
            if powerup in TILE_POWERUPS[tile_type]:
                if counts['next_all'][tile_type] == 0:
                    powerups_to_drop.append(powerup)

                if counts['next_ten'][tile_type] > 0 and powerup not in active_powerups_names:
                    powerups_to_activate.append(powerup)

        # RAIN POWERUPS
        if powerup == 'RemoveCloud' and counts['next_one'] == 1:
            powerups_to_activate.append(powerup)

        if powerup == 'Umbrella' and 'RemoveCloud' not in powerups_to_activate \
                and (counts['next_ten']['rain'] > 4 or counts['next_one']['rain'] == 1):
            powerups_to_activate.append(powerup)

    return powerups_to_activate, powerups_to_drop

