class Window:
    @staticmethod
    def is_point_in_window(point, len_x, len_y):
        return (point[0] >= 0 and point[0] <= len_x and point[1] >= 0 and point[1] <= len_y)  
    
    @staticmethod
    def is_point_off_window(point, len_x, len_y):
        return not Window.is_point_in_window(point, len_x, len_y)

    @staticmethod
    def translate_point(point, len_x, len_y):
        x, y = point[0], point[1]
        if x < 0:
            x = len_x
        if x > len_x:
            x = 0
        if y < 0:
            y = len_y
        if y > len_y:
            y = 0
        return (x, y)

    @staticmethod
    def translate_over_edge_func(center, point_lsts, c_trans_func, p_trans_func):
        target_center = c_trans_func(center)
        new_points_lists = []
        for p_lst in point_lsts:
            new_points = []
            for p in p_lst:
                np = p_trans_func(center, p)
                new_points.append(np)
            new_points_lists.append(new_points)
        return target_center, new_points_lists

    @staticmethod
    def translate_over_edge(config, center, points_lsts, buffer):
        screen_x = config['screen']['x']
        screen_y = config['screen']['y']
        min_x, min_y = 0 - buffer, 0 - buffer
        max_x, max_y = screen_x + buffer, screen_y + buffer
        if (center[1] < min_y):
            p_trans_func = lambda c, p: (p[0], max_y - (c[1] - p[1]))
            c_trans_func = lambda c: (c[0], max_y)
            return Window.translate_over_edge_func(center, points_lsts, c_trans_func, p_trans_func)
        if (center[1] > max_y):
            p_trans_func = lambda c, p: (p[0], min_y - (c[1] - p[1]))
            c_trans_func = lambda c: (c[0], min_y)
            return Window.translate_over_edge_func(center, points_lsts, c_trans_func, p_trans_func)
        if (center[0] < min_x):
            p_trans_func = lambda c, p: (max_x - (c[0] - p[0]), p[1])
            c_trans_func = lambda c: (max_x, c[1])
            return Window.translate_over_edge_func(center, points_lsts, c_trans_func, p_trans_func)
        if (center[0] > max_x):
            p_trans_func = lambda c, p: (min_x - (c[0] - p[0]), p[1])
            c_trans_func = lambda c: (min_x, c[1])
            return Window.translate_over_edge_func(center, points_lsts, c_trans_func, p_trans_func)
        return center, points_lsts