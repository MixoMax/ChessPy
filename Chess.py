import math
import pygame
import sys
import time
import PIL.Image

global field

class Field():
    def __init__(self):
        self.fields = [[None for i in range(8)] for j in range(8)]
        self._init_pawns()
        self.last_clicked = None
        self.last_moved = None
        self._load_image("assets/Board.png")
        self.check_turns_white = 0
        self.check_turns_black = 0
    
    def _init_pawns(self):
        pawn_positions = [
            ((i, 1), Pawn, "white") for i in range(8)
        ] + [
            ((i, 6), Pawn, "black") for i in range(8)
        ]

        other_pieces = [
            ((0, 0), Rock, "white"),
            ((7, 0), Rock, "white"),
            ((0, 7), Rock, "black"),
            ((7, 7), Rock, "black"),
            ((1, 0), Knight, "white"),
            ((6, 0), Knight, "white"),
            ((1, 7), Knight, "black"),
            ((6, 7), Knight, "black"),
            ((2, 0), Bishop, "white"),
            ((5, 0), Bishop, "white"),
            ((2, 7), Bishop, "black"),
            ((5, 7), Bishop, "black"),
            ((3, 0), Queen, "white"),
            ((3, 7), Queen, "black"),
            ((4, 0), King, "white"),
            ((4, 7), King, "black")
        ]

        for position, piece_type, color in pawn_positions + other_pieces:
            x, y = position
            self.fields[x][y] = piece_type(x, y, color)
    
    def _load_image(self, image):
        self.image = pygame.image.load(image)
    
    def draw(self, screen):
        screen.blit(self.image, (0,0))
        for i in range(8):
            for j in range(8):
                if self.fields[i][j] is not None:
                    #print(self.fields[i][j], "drawn at", i, j)
                    self.fields[i][j].draw(screen)
                    if isinstance(self.fields[i][j], King):
                        if self.fields[i][j].check() == True:
                            if self.fields[i][j].color == "white":
                                self.check_turns_white += 1
                                if self.check_turns_white == 1:
                                    print("White is in check!")
                                elif self.check_turns_white > 1:
                                    print("White is in checkmate!")
                            elif self.fields[i][j].color == "black":
                                self.check_turns_black += 1
                                if self.check_turns_black == 1:
                                    print("Black is in check!")
                                elif self.check_turns_black > 1:
                                    print("Black is in checkmate!")
    
    def click(self, mouse_pos):
        self.draw(screen)
        mouse_x, mouse_y = mouse_pos
        x, y = math.floor(mouse_x / 100), math.floor(mouse_y / 100)
        p = self.fields[x][y]
        if p is not None or self.last_clicked is not None:
            print(p, "clicked at", x, y)
            if self.last_clicked is not None:
                if (x,y) in self.last_clicked.possible_moves()[0]:
                    try:
                        if p.color == self.last_clicked.color:
                            return None
                    except:
                        pass
                    self.fields[x][y] = self.last_clicked
                    self.fields[self.last_clicked.x_pos][self.last_clicked.y_pos] = None
                    self.last_clicked.x_pos = x
                    self.last_clicked.y_pos = y
                    self.last_moved = self.last_clicked.color
                    self.last_clicked = None
                elif (x,y) in self.last_clicked.possible_moves()[1]:
                    try:
                        if p.color == self.last_clicked.color:
                            return None
                    except:
                        pass
                    self.fields[x][y] = self.last_clicked
                    self.fields[self.last_clicked.x_pos][self.last_clicked.y_pos] = None
                    self.last_clicked.x_pos = x
                    self.last_clicked.y_pos = y
                    self.last_moved = self.last_clicked.color
                    self.last_clicked = None
            if p is not None:
                p.highlight_moves(screen)
                self.last_clicked = p
        
        if p is None and self.last_clicked is not None:
            self.last_clicked = None
        
        if isinstance(p, Pawn):
            color = p.color
            # check if pawn is at the end of the field
            if color == "white" and y == 7:
                self.fields[x][y] = Queen(x, y, color)
            elif color == "black" and y == 0:
                self.fields[x][y] = Queen(x, y, color)
                


def filter_moves(moves: list, hits: list, color: str):
    for move in moves:
        x, y = move
        try:
            f = field.fields[x][y]
        except IndexError:
            moves.remove(move)
            continue
    for hit in hits:
        x, y = hit
        try:
            f = field.fields[x][y]
            if f.color == color:
                hits.remove(hit)
                continue
        except IndexError:
            hits.remove(hit)
            continue
    
    return moves, hits


class BasePiece():
    def __init__(self, x_pos, y_pos, color) -> None:
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.image = None
        self.color = color
        self.points = 0
    
    def draw(self, screen):
        img_pos = (self.x_pos * 100, self.y_pos * 100)
        screen.blit(self.image, img_pos)
    
    def _load_image(self, image):
        if self.color == "white":
            image = image.replace(".png", "_w.png")
        self.image = pygame.image.load(image)
        self.image = pygame.transform.scale(self.image, (100, 100))
            
        
    
    def possible_moves(self):
        pass
    
    def highlight_moves(self, screen):
        moves, hits = self.possible_moves()
        for move in moves:
            rect_surface = pygame.Surface((100, 100), pygame.SRCALPHA)
            color = (0, 255, 0, 128)  # Set alpha value to 128 for transparency
            rect_surface.fill(color)
            screen.blit(rect_surface, (move[0] * 100, move[1] * 100))
        for hit in hits:
            rect_surface = pygame.Surface((100, 100), pygame.SRCALPHA)
            color = (255, 0, 0, 128)  # Set alpha value to 128 for transparency
            rect_surface.fill(color)
            screen.blit(rect_surface, (hit[0] * 100, hit[1] * 100))

    def __str__(self) -> str:
        return f"{self.color} {self.__class__.__name__}"


class Pawn(BasePiece):
    def __init__(self, x_pos, y_pos, color) -> None:
        super().__init__(x_pos, y_pos, color)
        self._load_image("assets/pawn.png")
        self.points = 1
    
    def possible_moves(self):
        if self.color == "white":
            return self._possible_moves_white()
        else:
            return self._possible_moves_black()
    
    def _possible_moves_white(self):
        x, y = self.x_pos, self.y_pos
        hits = []
        moves = []
        try:
            if field.fields[x][y+1] == None:
                moves.append((x, y+1))
            if y == 1 and field.fields[x][y+1] == None and field.fields[x][y+2] == None:
                moves.append((x, y+2))
            if field.fields[x+1][y+1] != None:
                if field.fields[x+1][y+1].color != self.color:
                    hits.append((x+1, y+1))
            if field.fields[x-1][y+1] != None:
                if field.fields[x-1][y+1].color != self.color:
                    hits.append((x-1, y+1))
        except IndexError:
            pass
        moves = list(set(moves))
        hits = list(set(hits))
        if (x, y) in moves:
            moves.remove((x, y))
        if (x, y) in hits:
            hits.remove((x, y))
        moves, hits = filter_moves(moves, hits, self.color)
        return moves, hits
    
    def _possible_moves_black(self):
        x, y = self.x_pos, self.y_pos
        hits = []
        moves = []
        try:
            if field.fields[x][y-1] == None:
                moves.append((x, y-1))
            if y == 6 and field.fields[x][y-1] == None and field.fields[x][y-2] == None:
                moves.append((x, y-2))
            if field.fields[x+1][y-1] != None:
                if field.fields[x+1][y-1].color != self.color:
                    hits.append((x+1, y-1))
            if field.fields[x-1][y-1] != None:
                if field.fields[x-1][y-1].color != self.color:
                    hits.append((x-1, y-1))
        except IndexError:
            pass
        moves = list(set(moves))
        hits = list(set(hits))
        if (x, y) in moves:
            moves.remove((x, y))
        if (x, y) in hits:
            hits.remove((x, y))
        moves, hits = filter_moves(moves, hits, self.color)
        return moves, hits
            
class Rock(BasePiece):
    def __init__(self, x_pos, y_pos, color) -> None:
        super().__init__(x_pos, y_pos, color)
        self.points = 5
        self._load_image("assets/rock.png")
    
    def possible_moves(self):
        x, y = self.x_pos, self.y_pos
        moves = []
        hits = []

        def check_field(x, y):
            if field.fields[x][y] is None:
                moves.append((x, y))
            elif field.fields[x][y].color != self.color:
                hits.append((x, y))
                return True
            else:
                return True

        for i in range(x + 1, 8):
            if check_field(i, y):
                break

        for i in range(x - 1, -1, -1):
            if check_field(i, y):
                break

        for i in range(y + 1, 8):
            if check_field(x, i):
                break

        for i in range(y - 1, -1, -1):
            if check_field(x, i):
                break

        moves = list(set(moves))
        hits = list(set(hits))

        moves, hits = filter_moves(moves, hits, self.color)
        return moves, hits

class Knight(BasePiece):
    def __init__(self, x_pos, y_pos, color) -> None:
        super().__init__(x_pos, y_pos, color)
        self.points = 3
        self._load_image("assets/knight.png")
    
    def possible_moves(self):
        x, y = self.x_pos, self.y_pos
        moves, hits = [], []
        possible_positions = [(x+1, y+2), (x+1, y-2), (x-1, y+2), (x-1, y-2), (x+2, y+1), (x+2, y-1), (x-2, y+1), (x-2, y-1)]
        for pos in possible_positions:
            if pos[0] < 0 or pos[0] > 7 or pos[1] < 0 or pos[1] > 7:
                continue
            if field.fields[pos[0]][pos[1]] != None:
                hits.append(pos)
            else:
                moves.append(pos)
        moves = list(set(moves))
        hits = list(set(hits))
        if (x, y) in moves:
            moves.remove((x, y))
        if (x, y) in hits:
            hits.remove((x, y))
        moves, hits = filter_moves(moves, hits, self.color)
        return moves, hits

class Bishop(BasePiece):
    def __init__(self, x_pos, y_pos, color) -> None:
        super().__init__(x_pos, y_pos, color)
        self.points = 3
        self._load_image("assets/bishop.png")
    
    def possible_moves(self):
        x, y = self.x_pos, self.y_pos
        moves, hits = [], []
        for i in range(1, 8):
            pos = (x+i, y+i)
            if pos[0] > 7 or pos[0] < 0 or pos[1] > 7 or pos[1] < 0:
                continue
            if str(field.fields[x+i][y+i]).startswith(self.color):
                break
            elif field.fields[x+i][y+i] != None:
                hits.append(pos)
                break
            else:
                moves.append(pos)
        for i in range(1, 8):
            pos = (x+i, y-i)
            try:
                if str(field.fields[x+i][y-i]).startswith(self.color):
                    break
                elif field.fields[x+i][y-i] != None:
                    hits.append(pos)
                    break
                else:
                    moves.append(pos)
            except IndexError:
                pass
        for i in range(1, 8):
            pos = (x-i, y+i)
            try:
                if str(field.fields[x-i][y+i]).startswith(self.color):
                    break
                elif field.fields[x-i][y+i] != None:
                    hits.append(pos)
                    break
                else:
                    moves.append(pos)
            except IndexError:
                pass
        for i in range(1, 8):
            pos = (x-i, y-i)
            if str(field.fields[x-i][y-i]).startswith(self.color):
                break
            elif field.fields[x-i][y-i] != None:
                hits.append(pos)
                break
            else:
                moves.append(pos)
        moves = list(set(moves))
        hits = list(set(hits))
        if (x, y) in moves:
            moves.remove((x, y))
        if (x, y) in hits:
            hits.remove((x, y))
        moves, hits = filter_moves(moves, hits, self.color)
        return moves, hits
 
class Queen(BasePiece):
    def __init__(self, x_pos, y_pos, color) -> None:
        super().__init__(x_pos, y_pos, color)
        self.points = 9
        self._load_image("assets/queen.png")
    
    def possible_moves(self):
        x, y = self.x_pos, self.y_pos
        moves, hits = [], []
        for i in range(1, 8):
            pos = (x, i)
            if field.fields[x][i] != None:
                hits.append(pos)
                break
            else:
                moves.append(pos)
        for i in range(1, 8):
            pos = (i, y)
            if field.fields[i][y] != None:
                hits.append(pos)
                break
            else:
                moves.append(pos)
        for i in range(1, 8):
            pos = (x+i, y+i)
            if pos[0] > 7 or pos[0] < 0 or pos[1] > 7 or pos[1] < 0:
                continue
            if field.fields[x+i][y+i] != None:
                hits.append(pos)
                break
            else:
                moves.append(pos)
        for i in range(1, 8):
            pos = (x+i, y-i)
            try:
                if field.fields[x+i][y-i] != None:
                    hits.append(pos)
                    break
                else:
                    moves.append(pos)
            except:
                continue
        for i in range(1, 8):
            pos = (x-i, y+i)
            try:
                if field.fields[x-i][y+i] != None:
                    hits.append(pos)
                    break
                else:
                    moves.append(pos)
            except:
                pass
        for i in range(1, 8):
            pos = (x-i, y-i)
            if field.fields[x-i][y-i] != None:
                hits.append(pos)
                break
            else:
                moves.append(pos)
        moves = list(set(moves))
        hits = list(set(hits))
        if (x, y) in moves:
            moves.remove((x, y))
        if (x, y) in hits:
            hits.remove((x, y))
        moves, hits = filter_moves(moves, hits, self.color)
        return moves, hits

class King(BasePiece):
    def __init__(self, x_pos, y_pos, color) -> None:
        super().__init__(x_pos, y_pos, color)
        self.points = float("inf")
        self._load_image("assets/king.png")
    
    def possible_moves(self):
        x, y = self.x_pos, self.y_pos
        moves, hits = [], []
        possible_positions = [(x+1, y+1), (x+1, y-1), (x-1, y+1), (x-1, y-1), (x+1, y), (x-1, y), (x, y+1), (x, y-1)]
        for pos in possible_positions:
            if pos[0] < 0 or pos[0] > 7 or pos[1] < 0 or pos[1] > 7:
                continue
            if field.fields[pos[0]][pos[1]] != None:
                hits.append(pos)
            else:
                moves.append(pos)
        moves = list(set(moves))
        hits = list(set(hits))
        if (x, y) in moves:
            moves.remove((x, y))
        if (x, y) in hits:
            hits.remove((x, y))
        moves, hits = filter_moves(moves, hits, self.color)
        return moves, hits
    
    def check(self):
        x, y = self.x_pos, self.y_pos
        for i in range(8):
            for j in range(8):
                if field.fields[i][j] != None and field.fields[i][j].color != self.color:
                    hits = field.fields[i][j].possible_moves()[1]
                    if hits != []:
                        if (x, y) in hits:
                            return True
        return False

screen = pygame.display.set_mode((800, 800))
pygame.display.set_caption("Chess")
clock = pygame.time.Clock()
field = Field()
field.draw(screen)
pygame.display.update()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    click_pos = pygame.mouse.get_pos()
    if pygame.mouse.get_pressed()[0]:
        field.click(click_pos)
        
    clock.tick(60)
    pygame.display.update()