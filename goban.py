

import random
import pygame
import go
from sys import exit

FPS = 30

BACKGROUND = 'images/board_image.jpg'
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
        pygame.draw.circle(screen, self.color, self.coords, 18, 0)
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
        self.size = 9
        self.outline = pygame.Rect(45, 45, 320, 320)
        self.draw()


    #hiển thị bàn cờ
    def draw(self):
        """Draw the board to the background and blit it to the screen.

        The board is drawn by first drawing the outline, then the 19x19
        grid and finally by adding hoshi to the board. All these
        operations are done with pygame's draw functions.

        This method should only be called once, when initializing the
        board.

        """
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
                pygame.draw.circle(background, BLACK, coords, 5, 0)
        for i in range(9):
            font = pygame.font.Font(None, 18)
            text = font.render(str(i + 1), True, BLACK)
            text_rect = text.get_rect(center=(20, 45 + i * 40))
            background.blit(text, text_rect)
        letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J']
        for i in range(9):
            font = pygame.font.Font(None, 18)
            text = font.render(letters[i], True, BLACK)
            text_rect = text.get_rect(center=(45 + i * 40, 20))
            background.blit(text, text_rect)
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

    # Kiểm tra nước đi có hợp lệ
    def is_valid_move(self, move):
        x, y = move
        return 1 <= x <= self.size and 1 <= y <= self.size and not self.search(point=move)
    
    def is_game_over(self):
        game_over = not any(self.is_valid_move((i, j)) for i in range(self.size) for j in range(self.size))
        if game_over:
            pygame.time.delay(250)  # Wait for 1 second to display the popup
            pygame.display.set_mode((450,300))  # Set a small window for the popup
            font = pygame.font.Font(None, 36)
            text = font.render("Game Over!", True, (255, 128, 0))
            text_rect = text.get_rect(center=(220, 150))
            pygame.display.get_surface().blit(text, text_rect)
            pygame.display.flip()
            pygame.time.delay(5000)  # Display the popup for 5 seconds
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
                print("Human move: " + str(added_stone))
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
            print("AI move: " + str(added_computer_stone))
            board.update_liberties(added_computer_stone)

    def get_legal_moves(self):
        legal_moves = []
        for i in range(10):
            for j in range(10):
                if self.board.is_valid_move((i, j)):
                    legal_moves.append((i, j))
        return legal_moves

def main():

    clock = pygame.time.Clock()

    human_player = Human(board, BLACK)
    computer_player = Computer(board, WHITE)
    currentP = human_player
    while True:
        clock.tick(FPS)

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
                    #pygame.time.wait(500)
                    computer_player.make_move()
                    currentP = human_player

if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Cờ vây')
    screen = pygame.display.set_mode(BOARD_SIZE, 0, 32)
    background = pygame.image.load(BACKGROUND).convert()
    board = Board()
    main()
