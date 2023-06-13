# Importing required libraries
import pygame
import math
from queue import PriorityQueue

# Setting up window
WIDTH = 800
WINDOW = pygame.display.set_mode((WIDTH,WIDTH))
pygame.display.set_caption("A* Pathfinding Algorithm")

# Colors
WHITE = (255, 255, 255)
LIGHT_BLUE = (115, 215, 255)
BLACK = (0, 0, 0)
GREEN = (51, 255, 0)
RED = (255, 0, 0)
NAVY_BLUE = (0, 22, 82)
GREY = (61, 61, 61)
DARK_LIME = (127, 156, 2)
BLUE = (10, 26, 252)

# Setting up the grid functionality
class Spot:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self):
        return self.row, self.col

    def is_closed(self):
        return self.color == LIGHT_BLUE
    
    def is_open(self):
        return self.color == GREEN
    
    def is_barrier(self):
        return self.color == BLACK
    
    def is_start(self):
        return self.color == NAVY_BLUE

    def is_end(self):
        return self.color == RED 
    
    def reset(self):
        self.color = WHITE
    
    def make_start(self):
        self.color = DARK_LIME

    def make_closed(self):
        self.color = LIGHT_BLUE
    
    def make_open(self):
        self.color = BLUE

    def make_barrier(self):
        self.color = BLACK
    
    def make_end(self):
        self.color = RED
    
    def make_path(self):
        self.color = GREEN
    
    def draw(self, window):
        pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.width))
    
    def update_neighbors(self, grid):
        self.neighbors = []
        # Down
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.col])

        # Up
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row - 1][self.col])

        # Right
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col + 1])

        # Left
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False
    
def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()

def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = h(start.get_pos(), end.get_pos())
    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        current = open_set.get()[2]
        open_set_hash.remove(current)
        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True
        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1
            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()
        draw()
        if current != start:
            current.make_closed()
            
    return False

def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(width):
            spot = Spot(i, j, gap, rows)
            grid[i].append(spot)
    return grid

def draw_grid(window, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(window, GREY, (0, i *  gap), (width, i * gap))
        for j in range(width):
            pygame.draw.line(window, GREY, (j *  gap, 0), (j  * gap, width))

def draw(window, grid, rows, width):
    window.fill(WHITE)
    for row in grid:
        for spot in row:
            spot.draw(window)
    draw_grid(window, rows, width)
    pygame.display.update()

def get_clicked_pos(mouse_pos, rows, width):
    gap = width // rows
    y, x = mouse_pos
    row = y // gap
    col = x // gap
    return row, col

def main(window, width):
    ROWS = 50
    grid = make_grid(ROWS, width)
    start = None
    end = None
    running = True
    started = False
    while running:
        draw(window, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if pygame.mouse.get_pressed()[0]: # Left mouse button
                mouse_pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(mouse_pos, ROWS, width)
                spot = grid[row][col]
                if not start and spot != end:
                    start = spot
                    start.make_start()
                elif not end and spot != start:
                    end = spot
                    end.make_end()
                elif spot != end and spot != start:
                    spot.make_barrier()
            elif pygame.mouse.get_pressed()[2]: # Right mouse button
                mouse_pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(mouse_pos, ROWS, width)
                spot = grid[row][col]
                spot.reset()
                if spot == start:
                    start = None
                elif spot == end:
                    end = None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)
                    algorithm(lambda: draw(window, grid, ROWS, width), grid, start, end)
            
                if event.key == pygame.K_ESCAPE:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)


    pygame.quit()


main(WINDOW, WIDTH)