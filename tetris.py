import random
from tkinter import Tk, Canvas, ALL
from pynput.keyboard import Key, Listener
from multiprocessing import Process,Queue
import time

#smallest game board allowed
MIN_ALLOWED_WIDTH = 5
MIN_ALLOWED_HEIGHT = 5
class tetris():
    
    width = 15
    height = 30
    piece_lowering_interval = .15 #s between piece moves

    window_side_padding_x = 10
    window_side_padding_y = 10
    window_block_width = 40
    window_block_spacing = 4

    def __init__(self,width = None,height = None):
        if width:   self.width = width
        if height:  self.height = height
        self.create_new_game()
        return

    def create_new_game(self):
        self.create_grid()
        print('created grid')
        self.create_default_pieces()
        print('created default pieces')
        self.add_new_piece()
        print('added new piece')
        #self.create_keyboard_listener()
        #print('created keyboard listener')
        self.create_game_window()
        print('created window')
        self.draw()

    def create_grid(self):
        self.width      = max(self.width,MIN_ALLOWED_WIDTH)
        self.height     = max(self.height,MIN_ALLOWED_HEIGHT)

        self.grid           = [[0 for i in range(self.height)] for j in range(self.width)]
        self.grid_y_pos     = [[i for i in range(self.height)] for j in range(self.width)]
        self.grid_x_pos     = [[j for i in range(self.height)] for j in range(self.width)]
        self.grid_colors    = [["#505050" for i in range(self.height)] for j in range(self.width)]
        return

    def change_grid_size(self,width,height):
        self.width = width
        self.height = height
        self.create_new_game()
        return

    def create_default_pieces(self):
        self.pieces = []
        self.add_piece([(0,0),(1,0),(2,0),(3,0)])   # straight 1 x 4segment
        self.add_piece([(0,0),(1,0),(1,1),(0,1)])   # 2x2 cube
        self.add_piece([(0,0),(1,0),(2,0),(2,1)])   # left elbow
        self.add_piece([(0,0),(0,1),(0,2),(1,2)])   # right elbow
        self.add_piece([(0,0),(1,0),(1,1),(2,1)])   # first squiggle
        self.add_piece([(0,1),(1,1),(1,0),(2,0)])   # second squiggle

        return

    def create_game_window(self):
        self.window_width = self.window_side_padding_x*2 \
            + self.width * (self.window_block_width + self.window_block_spacing)\
            -self.window_block_spacing
        self.window_height = self.window_side_padding_y*2 \
            + self.height * (self.window_block_width + self.window_block_spacing)

        self.window_master = Tk()
        self.window = Canvas(self.window_master,width = self.window_width,height = self.window_height)
        self.window.pack()
        return

    def add_constant_window_elements(self):
        #TODO: Add border elements, framing, grid outline, and other permanent UI features
        
        return

    def close_game_window(self):
        try:
            self.window_master.destroy()
        except:
            return
        return

    def add_piece(self,points):
        self.pieces.append(points)
        return

    def get_random_piece(self):
        piece = random.randrange(len(self.pieces))
        return self.pieces[piece]

    def get_piece_bounds(self,piece):
        left_bound      = min([p[0] for p in piece])
        right_bound     = max([p[0] for p in piece])
        upper_bound    = max([p[1] for p in piece])
        lower_bound     = min([p[1] for p in piece])
        return [left_bound,right_bound,lower_bound,upper_bound]

    def add_new_piece(self):
        piece = self.get_random_piece()
        bounds = self.get_piece_bounds(piece)

        self.new_piece = piece
        self.new_piece_x = min(round(self.width/2) , self.width - bounds[1] - 1)
        self.new_piece_y = self.height - bounds[3] - 1

        return self.is_valid_piece_placement(self.new_piece,self.new_piece_x,self.new_piece_y)

    def is_valid_piece_placement(self,piece,x,y):
        bounds = self.get_piece_bounds(piece)

        left_oob    = x + bounds[0] < 0
        right_oob   = x + bounds[1] > self.width
        bot_oob     = y + bounds[2] < 0
        top_oob     = y + bounds[3] > self.height

        if left_oob or right_oob or bot_oob or top_oob:
            return False

        for (p_x,p_y) in self.new_piece:
            try:
                if self.grid[x+p_x][y+p_y]:
                    return False
            except IndexError:
                return False
        return True

    def rotate_piece_right(self):
        rotated_piece = [(j,-1*i) for (i,j) in self.new_piece]

        if self.is_valid_piece_placement(rotated_piece,self.new_piece_x,self.new_piece_y):
            self.new_piece = rotated_piece
            return True
        return False

    def rotate_piece_left(self):
        rotated_piece = [(-1*j,i) for (i,j) in self.new_piece]
        if self.is_valid_piece_placement(rotated_piece,self.new_piece_x,self.new_piece_y):
            self.new_piece = rotated_piece
            return True
        return False

    def move_piece_left(self):
        new_x = self.new_piece_x - 1
        if self.is_valid_piece_placement(self.new_piece,new_x,self.new_piece_y):
            self.new_piece_x = new_x
            return True
        return False

    def move_piece_right(self):
        new_x = self.new_piece_x + 1
        if self.is_valid_piece_placement(self.new_piece,new_x,self.new_piece_y):
            self.new_piece_x = new_x
            return True
        return False

    def move_piece_down(self):
        new_y = self.new_piece_y - 1
        if self.is_valid_piece_placement(self.new_piece,self.new_piece_x,new_y):
            self.new_piece_y = new_y
            return True
        else:
            for (x,y) in self.new_piece:
                self.grid[x+self.new_piece_x][y+self.new_piece_y] = 1
                self.check_grid_rows()
        return False
    
    def move_piece_ground(self):
        while self.move_piece_down():
            continue

    def check_grid_rows(self):
        row_num = -1
        while row_num < (self.height-1):
            row_num += 1
            row = [self.grid[i][row_num] for i in range(self.width)]
            row_full = True
            for cell in row: 
                if cell == 0: row_full = False

            if row_full:
                for col in range(self.width):
                    for shift_row in range(row_num+1,self.height):
                        self.grid[col][shift_row-1] = self.grid[col][shift_row]
                    self.grid[col][self.height - 1] = 0
                row_num -= 1     
        return

    def draw(self):
        #for col,x_col,y_col,color_col in zip(self.grid,self.grid_x_pos,self.grid_y_pos,self.grid_colors):
        #    for cell,x,y,color in zip(col,x_col,y_col,color_col):
        for i in range(self.width):
            for j in range(self.height):
                cell = self.grid[i][j]
                x = self.grid_x_pos[i][j]
                y = self.grid_y_pos[i][j]
                color = self.grid_colors[i][j]
                
                if cell == 1: 
                    #print(cell)
                    #print('(%d,%d)'%(x,y))
                    b_x = self.window_side_padding_x + x * (self.window_block_width + self.window_block_spacing)
                    b_y = self.window_height - self.window_side_padding_y - (y + 1) * (self.window_block_width + self.window_block_spacing)
                    self.window.create_rectangle(b_x,b_y,b_x + self.window_block_width, b_y + self.window_block_width,fill = color)

        for point in self.new_piece:
            x = self.window_side_padding_x + (point[0] +  self.new_piece_x) * (self.window_block_width + self.window_block_spacing)
            y = self.window_height - self.window_side_padding_y - (point[1] + self.new_piece_y + 1) * (self.window_block_width + self.window_block_spacing)
            self.window.create_rectangle(x,y,x + self.window_block_width,y + self.window_block_width,fill = "yellow")

        self.window_master.update()
        return

def run_interactive_keyboard(game):
    command = None
    command_queue = Queue()
    def on_press(key):
        if key == Key.up:
            command_queue.put('UP')
        elif key == Key.down:
            command_queue.put('DOWN')
        elif key == Key.right:
            command_queue.put('RIGHT')
        elif key == Key.left:
            command_queue.put('LEFT')
        else:
            command = key
        print('{0} pressed'.format(key))

    def on_release(key):
        print('{0} release'.format(key))
        if key == Key.esc:
            # Stop listener
            command_queue.put('STOP')
            return False

    # Collect events until released
    with Listener(on_press=on_press,on_release=on_release) as listener:
        running = True
        last_piece_lower = time.time()
        while running:
            if not command_queue.empty(): command  = command_queue.get_nowait()
            if not command == None:
                print('New Command: %s'%command)
                if command == 'STOP':
                    running = False
                elif command == 'UP':    game.rotate_piece_left()
                elif command == 'DOWN':  game.rotate_piece_right()
                elif command == 'LEFT':  game.move_piece_left()
                elif command == 'RIGHT': game.move_piece_right()
                command = None

            if time.time() - last_piece_lower > game.piece_lowering_interval:
                last_piece_lower = time.time()
                if not game.move_piece_down():
                    if not game.add_new_piece():
                        running = False # game over, can't add a new piece without blocking.
            
            try:
                game.window.delete(ALL)
                game.draw()
            except: running = False
        game.close_game_window()
    return

if __name__ == '__main__':
    game = tetris()
    run_interactive_keyboard(game)

        
