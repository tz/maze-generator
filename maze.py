import random
import sys
import yaml

from numpy import random as numpy_random
from PIL import Image, ImageDraw

try:
    config = yaml.safe_load(open('settings.yml', 'r'))
except yaml.YAMLError as exc:
    print(exc)
    sys.quit()

width = config['cell_width_in_px'] * config['cells_across'] + config['line_width_in_px']
height = config['cell_width_in_px'] * config['cells_down'] + config['line_width_in_px']
img = Image.new('RGB', (width, height), color=config['background_color'])
draw = ImageDraw.Draw(img)

m = []  # The Maze, a 2-D array of Cells
direction = None

class Cell:
    x = None
    y = None
    parentx = None
    parenty = None
    visited = False
    top_border = True
    left_border = True
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "{}, {}, {}visited. Parents: {}, {}".format(self.x, self.y, ("not " if not self.visited else ""), self.parentx, self.parenty)

relatives = {
    'L': {
        'ahead': 'L',
        'left': 'B',
        'right': 'A',
        'reverse': 'R',
    },
    'A': {
        'ahead': 'A',
        'left': 'L',
        'right': 'R',
        'reverse': 'B',
    },
    'R': {
        'ahead': 'R',
        'left': 'A',
        'right': 'B',
        'reverse': 'L',
    },
    'B': {
        'ahead': 'B',
        'left': 'R',
        'right': 'L',
        'reverse': 'A',
    }
}

# "Note that line joins are not handled well, so wide polylines
# will not look good." Use rectangles instead. Always stroke the
# lines down and to the right
def line(x1, y1, x2, y2):
    w = config['line_width_in_px']
    draw.rectangle([x1, y1, x2 + w, y2 + w], config['line_color'])


def draw_border():
    cell = config['cell_width_in_px']
    line_width = config['line_width_in_px']
    x = config['cells_across']
    y = config['cells_down']
    line(0, 0, 0, y * cell)
    line(0, 0, x * cell, 0)
    line(x * cell, 0, x * cell, y * cell)
    line(0, y * cell, x * cell , y * cell)

def get_unvisited_neighbors(x, y):
    neighbs = []
    # LEFT
    if (x > 0):
        if m[x-1][y].visited == False:
            neighbs.append([x-1,y, 'L'])
    # ABOVE
    if (y > 0):
        if m[x][y-1].visited == False:
            neighbs.append([x,y-1, 'A'])
    # RIGHT
    if (x < config['cells_across']-1):
        if m[x+1][y].visited == False:
            neighbs.append([x+1,y, 'R'])
    # BELOW
    if (y < config['cells_down']-1):
        if m[x][y+1].visited == False:
            neighbs.append([x,y+1, 'B'])
    return neighbs

def choose_neighbor(neighbs):
    if not direction:
        return random.choice(neighbs)

    ahead = config['move_ahead_weight']
    left = config['move_left_weight']
    right = config['move_right_weight']
    reverse = config['move_reverse_weight']

    choices = []
    probabilities = []
    total_probability_weights = 0
    for n in neighbs:
        if (n[2] == relatives[direction]['ahead']):
            total_probability_weights = total_probability_weights + ahead
            n.append(ahead)
        elif (n[2] == relatives[direction]['reverse']):
            total_probability_weights = total_probability_weights + reverse
            n.append(reverse)
        elif (n[2] == relatives[direction]['left']):
            total_probability_weights = total_probability_weights + left
            n.append(left)
        elif (n[2] == relatives[direction]['right']):
            total_probability_weights = total_probability_weights + right
            n.append(right)

    for n in neighbs:
        choices.append(n)
        probabilities.append(n[3]/total_probability_weights)

    choice_index= numpy_random.choice(len(choices), None, replace=False, p=probabilities)
    return choices[choice_index]

def build_maze(x, y):
    global direction
    while True:
        m[x][y].visited = True
        neighbs = get_unvisited_neighbors(x, y)

        # Backtrack when all neighbors visited
        if not neighbs:
            if x == 0 and y == 0:
                return;
            direction = None
            new_x = m[x][y].parentx
            y = m[x][y].parenty
            x = new_x
            continue;

        # As we walk, "knock down" walls
        neighbor = choose_neighbor(neighbs)
        if neighbor[2] == 'L':
            m[x][y].left_border = False;
        if neighbor[2] == 'A':
            m[x][y].top_border = False;
        if neighbor[2] == 'R':
            m[x+1][y].left_border = False;
        if neighbor[2] == 'B':
            m[x][y+1].top_border = False;
        direction = neighbor[2]
        m[neighbor[0]][neighbor[1]].parentx = x
        m[neighbor[0]][neighbor[1]].parenty = y
        x = neighbor[0]
        y = neighbor[1]

def draw_cell(x, y):
    w = config['cell_width_in_px']
    if m[x][y].left_border:
        line(x*w, y*w, x*w, y*w + w)
    if m[x][y].top_border:
        line(x*w, y*w, x*w + w, y*w)

def draw_maze():
    for row in m:
        for cell in row:
            draw_cell(cell.x, cell.y)

def main():
    global m
    draw_border()
    m = [[Cell(x,y) for y in range(config['cells_down'])] for x in range(config['cells_across'])]
    build_maze(0, 0)
    draw_maze()
    img.save('m.png')

if __name__ == "__main__":
    main()
