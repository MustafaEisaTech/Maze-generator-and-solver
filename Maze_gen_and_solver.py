import pygame
import sys
from queue import PriorityQueue
from random import choice
import time


pygame.init()
RES = WIDTH, HEIGHT = 1000, 600
#desktop_size = pygame.display.Info()
#w , h = desktop_size.current_w , desktop_size.current_h
#RES = WIDTH, HEIGHT = w, h
TILE = 40
cols, rows = WIDTH // TILE, HEIGHT // TILE


screen = pygame.display.set_mode(RES)
clock = pygame.time.Clock()
pygame.display.set_caption("Maze Generator & A* Solver")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
ORANGE = (255, 140, 0)
GRAY = (70, 70, 70)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

class Cell:
    _cell_count = 0
    
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.walls = {'top': True, 'right': True, 'bottom': True, 'left': True}
        self.visited = False
        self.id = Cell._cell_count
        Cell._cell_count += 1
    
    def draw(self, color=GRAY):
        x, y = self.x * TILE, self.y * TILE
        pygame.draw.rect(screen, color, (x, y, TILE, TILE))
        
        if self.walls['top']:
            pygame.draw.line(screen, ORANGE, (x, y), (x + TILE, y), 2)
        if self.walls['right']:
            pygame.draw.line(screen, ORANGE, (x + TILE, y), (x + TILE, y + TILE), 2)
        if self.walls['bottom']:
            pygame.draw.line(screen, ORANGE, (x, y + TILE), (x + TILE, y + TILE), 2)
        if self.walls['left']:
            pygame.draw.line(screen, ORANGE, (x, y), (x, y + TILE), 2)
            
        if self == start_cell:  
            pygame.draw.circle(screen, GREEN, (x + TILE//2, y + TILE//2), TILE//3)
        elif self == end_cell:  
            pygame.draw.circle(screen, RED, (x + TILE//2, y + TILE//2), TILE//3)
    
    def check_neighbors(self):
        neighbors = []
        directions = {
            'top': (self.x, self.y - 1),
            'right': (self.x + 1, self.y),
            'bottom': (self.x, self.y + 1),
            'left': (self.x - 1, self.y)
        }
        for direction, (nx, ny) in directions.items():
            if 0 <= nx < cols and 0 <= ny < rows:
                neighbor = grid_cells[nx + ny * cols]
                if not neighbor.visited:
                    neighbors.append((direction, neighbor))
        return choice(neighbors) if neighbors else None

    def get_accessible_neighbors(self):
        neighbors = []
        directions = {
            'top': (self.x, self.y - 1),
            'right': (self.x + 1, self.y),
            'bottom': (self.x, self.y + 1),
            'left': (self.x - 1, self.y)
        }
        for direction, (nx, ny) in directions.items():
            if 0 <= nx < cols and 0 <= ny < rows:
                if not self.walls[direction]:
                    neighbor = grid_cells[nx + ny * cols]
                    neighbors.append((direction, neighbor))
        return neighbors

def generate_maze():
    current_cell = choice(grid_cells)
    stack = []
    
    while True:
        current_cell.visited = True
        current_cell.draw(BLACK)
        
        start_cell.draw(BLACK)
        end_cell.draw(BLACK)
        
        pygame.display.flip()
        #time.sleep(0.02)
        
        next_data = current_cell.check_neighbors()
        
        if next_data:
            direction, next_cell = next_data
            stack.append(current_cell)
            remove_walls(current_cell, next_cell, direction)
            current_cell = next_cell
        elif stack:
            current_cell = stack.pop()
        else:
            break

def heuristic(cell1, cell2):
    return abs(cell1.x - cell2.x) + abs(cell1.y - cell2.y)

def a_star_search(start, goal):
    path = []  
    open_set = PriorityQueue()
    open_set.put((0, start.id, start))
    came_from = {}
    g_score = {cell: float('inf') for cell in grid_cells}
    g_score[start] = 0
    f_score = {cell: float('inf') for cell in grid_cells}
    f_score[start] = heuristic(start, goal)
    open_set_hash = {start}
    
    
    visited_cells = set()

    while not open_set.empty():
        current = open_set.get()[2]
        open_set_hash.remove(current)
        
        if current not in [start, goal]:
            current.draw(YELLOW)
        visited_cells.add(current)
        
        for cell in visited_cells:
            if cell not in [start, goal] and cell not in path:
                cell.draw(BLUE)
        
        start.draw(BLACK)
        goal.draw(BLACK)
        
        pygame.display.flip()
        time.sleep(0.0001)

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1]
        
        for direction, neighbor in current.get_accessible_neighbors():
            temp_g_score = g_score[current] + 1
            
            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + heuristic(neighbor, goal)
                if neighbor not in open_set_hash:
                    open_set.put((f_score[neighbor], neighbor.id, neighbor))
                    open_set_hash.add(neighbor)
    
    return []

def remove_walls(current, next, direction):
    if direction == 'top':
        current.walls['top'], next.walls['bottom'] = False, False
    elif direction == 'right':
        current.walls['right'], next.walls['left'] = False, False
    elif direction == 'bottom':
        current.walls['bottom'], next.walls['top'] = False, False
    elif direction == 'left':
        current.walls['left'], next.walls['right'] = False, False

def animate_solution(path):
    if not path:
        return
    
    for cell in grid_cells:
        cell.draw(BLACK)
    
    for i in range(len(path)):
        current_path = path[:i+1]
        
        for cell in grid_cells:
            if cell not in current_path:
                cell.draw(BLACK)
        
        for cell in current_path:
            cell.draw(GREEN)
        
        start_cell.draw(BLACK)
        end_cell.draw(BLACK)
        
        pygame.display.flip()
        time.sleep(0.03)

def get_random_cells():
    all_positions = [(x, y) for x in range(cols) for y in range(rows)]
    start_pos = choice(all_positions)
    all_positions.remove(start_pos)  
    end_pos = choice(all_positions)
    
    start = grid_cells[start_pos[0] + start_pos[1] * cols]
    end = grid_cells[end_pos[0] + end_pos[1] * cols]
    
    return start, end

Cell._cell_count = 0
grid_cells = [Cell(x, y) for y in range(rows) for x in range(cols)]
start_cell, end_cell = None, None  
path = []


font = pygame.font.Font(None, 36)
generate_text = font.render("Generate Maze", True, WHITE)
solve_text = font.render("Solve Maze", True, WHITE)
exit_text = font.render("Exit", True, WHITE)

generate_button = pygame.Rect(50, HEIGHT - 50, 180, 40)
exit_button = pygame.Rect(50, HEIGHT - 100, 180, 40)
solve_button = pygame.Rect(WIDTH - 230, HEIGHT - 50, 180, 40)


running = True
maze_generated = False
while running:
    screen.fill(GRAY)
    [cell.draw() for cell in grid_cells]
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if generate_button.collidepoint(event.pos):
                Cell._cell_count = 0
                grid_cells = [Cell(x, y) for y in range(rows) for x in range(cols)]
                start_cell, end_cell = get_random_cells()  
                generate_maze()
                maze_generated = True
                path = []
            elif solve_button.collidepoint(event.pos) and maze_generated:
                path = a_star_search(start_cell, end_cell)
                if path:
                    animate_solution(path)
            elif exit_button.collidepoint(event.pos) :
                pygame.quit()
                sys.exit()
    
    
    for cell in grid_cells:
        cell.draw(BLACK)
    
    for cell in path:
        cell.draw(GREEN)
        
    if start_cell and end_cell:
        start_cell.draw(BLACK)
        end_cell.draw(BLACK)

    pygame.draw.rect(screen, BLACK, generate_button)
    pygame.draw.rect(screen, BLACK, solve_button)
    pygame.draw.rect(screen, BLACK, exit_button)
    
    screen.blit(generate_text, (generate_button.x + 10, generate_button.y + 5))
    screen.blit(solve_text, (solve_button.x + 10, solve_button.y + 5))
    screen.blit(exit_text, (exit_button.x + 10, exit_button.y + 5))


    pygame.display.flip()
    clock.tick(480)