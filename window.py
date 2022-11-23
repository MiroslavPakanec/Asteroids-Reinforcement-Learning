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