import random
import pygame
import go
from sys import exit

BACKGROUND = 'images/ramin.jpg'
BOARD_SIZE = (410, 410)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


class Stone(go.Stone):
    def __init__(self, board, point, color):
        """Create, initialize and draw a stone."""
        super(Stone, self).__init__(board, point, color)
        self.coords = (5 + self.point[0] * 40, 5 + self.point[1] * 40)
        self.draw()

    def draw(self):
        """Draw the stone as a circle."""
        pygame.draw.circle(screen, self.color, self.coords, 17, 0)
        pygame.display.update()

    def remove(self):
        """Remove the stone from board."""
        blit_coords = (self.coords[0] - 20, self.coords[1] - 20)
        area_rect = pygame.Rect(blit_coords, (40, 40))
        screen.blit(background, blit_coords, area_rect)
        pygame.display.update()
        super(Stone, self).remove()


class Board(go.Board):
    def __init__(self):
        """Create, initialize and draw an empty board."""
        super(Board, self).__init__()
        self.size = 8 
        self.outline = pygame.Rect(45, 45, 320, 320)
        self.draw()

    def draw(self):

        pygame.draw.rect(background, BLACK, self.outline, 3)
        # Outline is inflated here for future use as a collidebox for the mouse
        self.outline.inflate_ip(20, 20)
        for i in range(8):
            for j in range(8):
                rect = pygame.Rect(45 + (40 * i), 45 + (40 * j), 40, 40)
                pygame.draw.rect(background, BLACK, rect, 1)
        for i in range(2):
            for j in range(2):
                coords = (125 + (160 * i), 125 + (160 * j))
                pygame.draw.circle(background, BLACK, coords, 3, 0)
        screen.blit(background, (0, 0))
        pygame.display.update()

    def update_liberties(self, added_stone=None):
        """Updates the liberties of the entire board, group by group.

        Usually a stone is added each turn. To allow killing by 'suicide',
        all the 'old' groups should be updated before the newly added one.

        """
        for group in self.groups:
            if added_stone:
                if group == added_stone.group:
                    continue
            group.update_liberties()
        if added_stone:
            added_stone.group.update_liberties()

    def is_valid_move(self, move):
        x, y = move
        return 0 <= x < self.size and 0 <= y < self.size and not self.search(point=move)
    
    def is_game_over(self):
        game_over = not any(self.is_valid_move((i, j)) for i in range(self.size) for j in range(self.size))
        if game_over:
            pygame.time.delay(1000)  # Wait for 1 second to display the popup
            pygame.display.set_mode((300, 100))  # Set a small window for the popup
            pygame.display.set_caption("Game Over")
            font = pygame.font.Font(None, 36)
            text = font.render("Game Over!", True, (255, 0, 0))
            text_rect = text.get_rect(center=(150, 150))
            pygame.display.get_surface().blit(text, text_rect)
            pygame.display.flip()
            pygame.time.delay(3000)  # Display the popup for 3 seconds
            exit()

        return game_over


class Human:
    def __init__(self, board, color):
        self.board = board
        self.color = color

    def make_move(self, event):
        if event.button == 1 and board.outline.collidepoint(event.pos):
            x = int(round(((event.pos[0] - 5) / 40.0), 0))
            y = int(round(((event.pos[1] - 5) / 40.0), 0))
            stone = board.search(point=(x, y))
            if stone:
                stone.remove()
            else:
                added_stone = Stone(board, (x, y), BLACK)
                self.board.update_liberties(added_stone)


class Computer:
    def __init__(self, board, color):
        self.board = board
        self.color = color

    def make_move(self):
        legal_moves = self.get_legal_moves()
        if legal_moves:
            move = random.choice(legal_moves)
            added_computer_stone = Stone(self.board, move, self.color)
            self.board.update_liberties(added_computer_stone)

    def get_legal_moves(self):
        legal_moves = []
        for i in range(8):
            for j in range(8):
                if self.board.is_valid_move((i, j)):
                    legal_moves.append((i, j))
        return legal_moves
    

def main():
    human_player = Human(board, BLACK)
    computer_player = Computer(board, WHITE)

    currentP = computer_player
    while True:
        pygame.time.wait(250)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if not board.is_game_over():   
                if(currentP == human_player):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        human_player.make_move(event)
                        currentP = computer_player
                else:
                    computer_player.make_move()
                    currentP = human_player

    

if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Goban')
    screen = pygame.display.set_mode(BOARD_SIZE, 0, 32)
    background = pygame.image.load(BACKGROUND).convert()
    board = Board()
    main()