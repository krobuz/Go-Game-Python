

import random
import time
import pygame
import go
from sys import exit

FPS = 0
TIMEOUT_SECONDS = 5

BACKGROUND = 'images/board_image.png'
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

    def make_temporary_move(self, move, color):
        x, y = move
        if self.is_valid_move(move):
            stone = Stone(self, move, color)
            self.update_liberties(stone)  # Update liberties for the new stone
            self.next = BLACK if color == WHITE else WHITE  # Switch the turn
        # else:
        #     raise ValueError("Invalid move: {}".format(move))

    def undo_temporary_move(self, move):
        x, y = move
        stone = self.search(point=move)
        if stone:
            stone.remove()  # Remove the stone from the board
            self.next = BLACK if stone.color == WHITE else WHITE  # Switch back the turn
        # else:
        #     raise ValueError("No stone found at position: {}".format(move))
            

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
            pygame.time.delay(500)  # Wait for 0.5 second to display the popup
            pygame.display.set_mode((450,300))  # Set a small window for the popup
            font = pygame.font.Font(None, 36)
            text = font.render("Game Over!", True, (255, 30, 70))
            text_rect = text.get_rect(center=(220, 150))
            pygame.display.get_surface().blit(text, text_rect)
            pygame.display.flip()
            pygame.time.delay(1000)  # Display the popup for 1 seconds
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
    def __init__(self, board, color, max_depth = 2):
        self.board = board
        self.color = color
        self.max_depth = max_depth
        self.last_move = None

    def get_opponent_color(self):
        return BLACK if self.color == WHITE else BLACK
    
    # def make_move(self):
    #     legal_moves = self.get_legal_moves()
    #     if legal_moves:
    #         #move = random.choice(legal_moves)    
    #         best_move = self.minimax(self.max_depth, True)[1]
    #         while best_move == self.last_move:
    #             best_move = self.minimax(self.max_depth, True)[1]
                
    #         added_computer_stone = Stone(self.board, best_move, self.color)
    #         print("AI move: " + str(added_computer_stone))
    #         self.last_move = best_move
    #         board.update_liberties(added_computer_stone)
    #     else:
    #         print("No legal moves for the computer.")

    def make_move(self):
        start_time = time.time()
        legal_moves = self.get_legal_moves()

        if legal_moves:
            best_move = self.minimax_with_timeout(self.max_depth-1, True, start_time)

            if best_move is not None:
                added_computer_stone = Stone(self.board, best_move, self.color)
                print("AI move: " + str(added_computer_stone))
                self.last_move = best_move
                self.board.update_liberties(added_computer_stone)
            else:
                print("Random move due to timeout.")
                self.make_random_move()
        else:
            print("No legal moves for the computer.")

    def make_random_move(self):
        legal_moves = self.get_legal_moves()
        if legal_moves:
            random_move = random.choice(legal_moves)
            added_computer_stone = Stone(self.board, random_move, self.color)
            print("Random move: " + str(added_computer_stone))
            self.last_move = random_move
            self.board.update_liberties(added_computer_stone)
        else:
            print("No legal moves for the computer.")
    def minimax_with_timeout(self, depth, maximizing_player, start_time):
        max_eval = float('-inf')
        best_move = None

        legal_moves = self.get_legal_moves()

        for move in legal_moves:
            self.board.make_temporary_move(move, self.get_opponent_color())
            eval, _ = self.minimax(depth - 1, False)
            self.board.undo_temporary_move(move)

            if eval > max_eval:
                max_eval = eval
                best_move = move

            # Check if time limit has been exceeded
            elapsed_time = time.time() - start_time
            if elapsed_time > TIMEOUT_SECONDS:
                return None

        return best_move
    
    def minimax(self, depth, maximizing_player):
        if depth == 0 or self.board.is_game_over():
            return self.evaluate_board(), None

        legal_moves = self.get_legal_moves()

        if maximizing_player:
            max_eval = float('-inf')
            best_move = None
            for move in legal_moves:
                self.board.make_temporary_move(move, self.get_opponent_color())
                eval, _ = self.minimax(depth - 1, False)
                self.board.undo_temporary_move(move)
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
            return max_eval, best_move
        else:
            min_eval = float('inf')
            best_move = None
            for move in legal_moves:
                self.board.make_temporary_move(move, self.color)
                eval, _ = self.minimax(depth - 1, True)
                self.board.undo_temporary_move(move)
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
            return min_eval, best_move

    def evaluate_board(self):
        computer = 0
        human = 0

        for group in self.board.groups:
            if group.stones and group.stones[0].color == self.color:
                computer += 1
                if len(group.liberties) == 1:
                    # Penalty for a group with only one liberty
                    computer -= 0.5  # Adjust the penalty as needed
            elif group.stones and group.stones[0].color == self.get_opponent_color():
                human += 1

        return computer - human
    
    def is_suicide_move(self, move):
        # Check if making the move would result in the computer's group having zero liberties
        self.board.make_temporary_move(move, self.color)
        is_suicide = len(self.board.groups[-1].liberties) == 0
        self.board.undo_temporary_move(move)
        return is_suicide
    
    def get_legal_moves(self):
        legal_moves = []
        for i in range(self.board.size):
            for j in range(self.board.size):
                move = (i, j)
                if self.board.is_valid_move(move) and not self.is_suicide_move(move):
                    legal_moves.append(move)
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
                    #pygame.time.wait(250)
                    computer_player.make_move()
                    currentP = human_player

if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Cờ vây')
    screen = pygame.display.set_mode(BOARD_SIZE, 0, 32)
    background = pygame.image.load(BACKGROUND).convert()
    board = Board()
    main()
