def action_to_move(action):
    action_map = {
        #   W A D S C
        0:  [0,0,0,0,0], # -
        1:  [1,0,0,0,0], # W
        2:  [0,1,0,0,0], # A
        3:  [0,0,1,0,0], # D
        4:  [0,0,0,0,1], # CTRL
        5:  [1,1,0,0,0], # W + A
        6:  [1,0,1,0,0], # W + D
        7:  [1,0,0,0,1], # W + CTRL
        8:  [1,1,0,0,1], # W + A + CTRL
        9:  [1,0,1,0,1], # W + D + CTRL
        10: [0,1,0,0,1], # A + CTRL
        11: [0,0,1,0,1], # D + CTRL
        12: [1,0,0,1,0], # W + SPACE
        13: [1,1,0,1,0], # W + A + SPACE
        14: [1,0,1,1,0], # W + D + SAPCE
        15: [1,0,0,1,1], # W + CTRL + SPACE
        16: [1,1,0,1,1], # W + A + CTRL + SPACE
        17: [1,0,1,1,1]  # W + D + CTRL + SPACE
    }
    return action_map[action]