"""
Module game Caro tích hợp AI sử dụng Pygame.

Trò chơi hoạt động với nền bàn cờ tiêu chuẩn 15x15, mục tiêu chiến thắng là tạo thành một đường thẳng
(ngang, dọc, chéo) gồm ít nhất 5 quân cờ liên tiếp.

Tính năng chính:
    - PvP: Hai người chơi đối đầu trực tiếp, luân phiên lượt đánh (X và O).
    - PvAI: Người chơi thi đấu với AI thông minh.

CTDL & Giải thuật cốt lõi:
    - Mảng 2D: Lưu trạng thái bàn cờ, truy xuất tọa độ với độ phức tạp O(1).
    - Win/Lose Detection: Duyệt cục bộ 4 hướng từ nước đi cuối cùng.
    - Minimax & Alpha-Beta Pruning: Tìm kiếm cây trò chơi và cắt tỉa nhánh.
    - Heuristic & Candidate Selection: Lượng giá cục diện và nước đi nhằm tìm ra nước đi tiềm năng.
"""

import pygame
import sys
import random

try:
    from Caro_ai import CaroAI
except ImportError:
    class CaroAI:
        """
        Lớp AI mặc định được sử dụng trong trường hợp không tìm thấy module Caro_ai
        """
        def best_moves(self, board):
            for r in range(15):
                for c in range(15):
                    if board[r][c] == "": return (r, c)
            return None

pygame.init()

WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Caro Game - Digital Circus")

try:
    raw_main = pygame.image.load("bg_main.png")
    raw_select = pygame.image.load("bg_select.png")
    raw_play = pygame.image.load("bg_play.png")
    
    BG_MAIN = pygame.transform.scale(raw_main, (WIDTH, HEIGHT))
    BG_SELECT = pygame.transform.scale(raw_select, (WIDTH, HEIGHT))
    BG_PLAY = pygame.transform.scale(raw_play, (WIDTH, HEIGHT))
except Exception as e:
    print(f"Lỗi tải ảnh nền: {e}")
    BG_MAIN = BG_SELECT = BG_PLAY = None

try:
    raw_pvp_x = pygame.image.load("Player_X.png")       
    raw_pvp_o = pygame.image.load("Player_O.png")      
    raw_pva_win = pygame.image.load("You_win.png")   
    raw_pva_lose = pygame.image.load("You_lose.png")
    
    POPUP_PVP_X = pygame.transform.scale(raw_pvp_x, (800, 160))
    POPUP_PVP_O = pygame.transform.scale(raw_pvp_o, (800, 160))
    POPUP_PVA_WIN = pygame.transform.scale(raw_pva_win, (800, 160))
    POPUP_PVA_LOSE = pygame.transform.scale(raw_pva_lose, (800, 160))
except Exception as e:
    print(f"Lỗi tải ảnh Pop-up: {e}")
    POPUP_PVP_X = POPUP_PVP_O = POPUP_PVA_WIN = POPUP_PVA_LOSE = None


try:
    raw_draw = pygame.image.load("TIE.png")
        
    POPUP_DRAW = pygame.transform.scale(raw_draw, (800, 160))
except Exception as e:
    print(f"Lỗi tải ảnh Pop-up Hòa: {e}")
    POPUP_DRAW = None

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (231, 76, 60)
BLUE = (52, 152, 219)
GOLD = (255, 255, 0)         
LIGHT_YELLOW = (255, 255, 180) 
GRID_COLOR = (200, 200, 200)

DARK_OVERLAY = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
DARK_OVERLAY.fill((0, 0, 0, 160))

try:
    font_huge = pygame.font.Font("SigmarOne-Regular.ttf", 70)
    font_large = pygame.font.Font("SigmarOne-Regular.ttf", 50)
    font_small = pygame.font.Font("SigmarOne-Regular.ttf", 26)
    font_win = pygame.font.Font("SigmarOne-Regular.ttf", 60)
except Exception as e:
    print(f"Không tìm thấy SigmarOne-Regular.ttf. Lỗi: {e}")
    font_huge = pygame.font.SysFont("Impact", 70)
    font_large = pygame.font.SysFont("Impact", 50)
    font_small = pygame.font.SysFont("Arial", 24, bold=True)
    font_win = pygame.font.SysFont("Impact", 60)

class GlowText:
    """
    Đối tượng văn bản có hiệu ứng phát sáng (Glow) khi người dùng di chuột lên.

    Attributes:
        text (str): Nội dung văn bản hiển thị.
        font (pygame.font.Font): Font chữ sử dụng để render.
        base_color (tuple): Màu mặc định của chữ (R, G, B).
        hover_color (tuple): Màu của chữ khi được trỏ chuột vào.
        glow_color (tuple): Màu hào quang phát sáng xung quanh chữ.
        main_surf (pygame.Surface): Bề mặt (surface) chứa text mặc định.
        rect (pygame.Rect): Khung giới hạn vị trí và va chạm của text.
        is_hovered (bool): Trạng thái kiểm tra xem chuột có đang trỏ vào nút hay không.
    """
    def __init__(self, x, y, text, font, base_color, hover_color, glow_color):
        """
        Khởi tạo đối tượng GlowText.

        Args:
            x (int): Tọa độ tâm X của văn bản.
            y (int): Tọa độ tâm Y của văn bản.
            text (str): Chuỗi nội dung hiển thị.
            font (pygame.font.Font): Đối tượng font của Pygame.
            base_color (tuple): Mã màu RGB mặc định.
            hover_color (tuple): Mã màu RGB khi di chuột (hover).
            glow_color (tuple): Mã màu RGB của lớp viền sáng.
        """
        self.text = text
        self.font = font
        self.base_color = base_color
        self.hover_color = hover_color
        self.glow_color = glow_color
        
        self.main_surf = self.font.render(self.text, True, self.base_color)
        self.rect = self.main_surf.get_rect(center=(x, y))
        self.is_hovered = False

    def draw(self, screen):
        """
        Vẽ chữ và hiệu ứng phát sáng lên màn hình

        Args:
            screen (pygame.Surface): Bề mặt màn hình game.
        """
        if self.is_hovered:
            for radius in range(5, 0, -1):
                glow_surf = self.font.render(self.text, True, self.glow_color)
                alpha_value = 50 if radius == 5 else (80 if radius == 3 else 150)
                glow_surf.set_alpha(alpha_value)
                
                for dx in [-radius, 0, radius]:
                    for dy in [-radius, 0, radius]:
                        if dx == 0 and dy == 0: continue
                        rect = glow_surf.get_rect(center=(self.rect.centerx + dx, self.rect.centery + dy))
                        screen.blit(glow_surf, rect)
            
            current_surf = self.font.render(self.text, True, self.hover_color)
        else:
            current_surf = self.main_surf

        screen.blit(current_surf, current_surf.get_rect(center=self.rect.center))

    def handle_event(self, event):
        """
        Xử lý sự kiện di chuột trên đối tượng text.

        Args: 
            event (pygame.event.Event): Sự kiện được lấy từ hàng đợi của Pygame.
        
        Returns:
            bool: True nếu người dùng di chuột vào nút, ngược lại là False.
        """
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and self.is_hovered:
            return True
        return False

class CaroGame:
    """
    Quản lý logic, trạng thái và giao diện của trò chơi Caro.

    Attributes:
        state (str): Trạng thái hiện tại của game ("MENU", "MODE_SELECT", "PLAYING").
        board_size (int): Số lượng ô trên một cạnh của bàn cờ (mặc định 15x15).
        board_width (int): Kích thước chiều rộng/cao của toàn bộ bàn cờ (pixel).
        square_size (int): Kích thước của mỗi ô vuông con (pixel).
        board_x (int): Tọa độ góc trên bên trái của bàn cờ (trục X).
        board_y (int): Tọa độ góc trên bên trái của bàn cờ (trục Y).
        board (list of list of str): Ma trận lưu trữ các nước đi ("X", "O", hoặc "").
        current_player (str): Lượt của người chơi hiện tại ("X" hoặc "O").
        winner (str or None): Người chiến thắng ("X", "O", "DRAW", hoặc None).
        game_mode (str): Chế độ chơi ("PvP" hoặc "PvAI").
        time_limit (int): Thời gian giới hạn cho mỗi lượt đi (giây).
        start_ticks (int): Mốc thời gian bắt đầu lượt đi hiện tại (millisecond).
        game_over (bool): Trạng thái cờ báo hiệu trò chơi đã kết thúc.
    """
    def __init__(self):
        """
        Khởi tạo thông số cơ bản và nút bấm cho game.
        """
        self.state = "MENU"
        self.board_size = 15
        self.board_width = 600  
        self.square_size = self.board_width // self.board_size
        self.board_x = 100       
        self.board_y = 60       
        
        self.play_btn = GlowText(640, 533, "CLICK TO PLAY", font_large, WHITE, LIGHT_YELLOW, GOLD)
        self.pvp_btn = GlowText(640, 366, "PLAYER VS PLAYER", font_large, WHITE, LIGHT_YELLOW, GOLD)
        self.pva_btn = GlowText(640, 500, "PLAYER VS AI", font_large, WHITE, LIGHT_YELLOW, GOLD)
        self.reset_btn = GlowText(1166, 53, "RESET", font_small, WHITE, RED, GOLD)
        self.play_again_btn = GlowText(640, 530, "PLAY AGAIN", font_large, WHITE, LIGHT_YELLOW, GOLD)
        
        self.reset_game()

    def reset_game(self):
        """
        Đặt lại toàn bộ dữ liệu về trạng thái ban đầu của game để bắt đầu ván mới.
        """
        self.board = [["" for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.current_player = "X"
        self.winner = None
        self.game_mode = "PvP"
        self.time_limit = 15
        self.start_ticks = pygame.time.get_ticks()
        self.game_over = False

    def check_win(self, r, c):
        """
        Kiểm tra trạng thái thắng/thua sau khi đánh một quân cờ.

        Thuật toán duyệt vết theo 4 hướng (ngang, dọc, 2 chéo) tính từ tọa độ
        vừa đánh để đếm số quân liên tiếp.

        Returns:
            bool: Trả về True nếu có đủ 5 quân liên tiếp, ngược lại False.
        """

        player = self.board[r][c]
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

        for dr, dc in directions:
            count = 1
            nr, nc = r + dr, c + dc
            while 0 <= nr < self.board_size and 0 <= nc < self.board_size and self.board[nr][nc] == player:
                count += 1
                nr += dr; nc += dc
            
            nr, nc = r - dr, c - dc
            while 0 <= nr < self.board_size and 0 <= nc < self.board_size and self.board[nr][nc] == player:
                count += 1
                nr -= dr; nc -= dc

            if count >= 5: return True
        return False
    
    def check_draw(self):
        """Kiểm tra điều kiện hòa (bàn cờ đã kín chỗ và không ai thắng).

        Returns:
            bool: True nếu không còn ô trống nào trên bàn cờ, ngược lại là False.
        """
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board[row][col] == "":
                    return False
        return True

    def draw_x(self, screen, r, c):
        """
        Vẽ biểu tượng quân X (màu đỏ) tại ô được chỉ định
        """
        cx = self.board_x + c * self.square_size + self.square_size // 2
        cy = self.board_y + r * self.square_size + self.square_size // 2
        offset = self.square_size // 3 
        pygame.draw.line(screen, RED, (cx - offset, cy - offset), (cx + offset, cy + offset), 4)
        pygame.draw.line(screen, RED, (cx + offset, cy - offset), (cx - offset, cy + offset), 4)

    def draw_o(self, screen, r, c):
        """
        Vẽ biểu tượng quân O (màu xanh) tại ô được chỉ định
        """
        cx = self.board_x + c * self.square_size + self.square_size // 2
        cy = self.board_y + r * self.square_size + self.square_size // 2
        pygame.draw.circle(screen, BLUE, (cx, cy), self.square_size // 2.5, 4)

    def draw_screens(self, screen, time_left):
        """
        Render toàn bộ hình ảnh, nút bấm và bảng thông báo theo trạng thái game.

        Args:
            screen (pygame.Surface): bề mặt màn hình chính cần vẽ lên.
            time_left (float): thời gian còn lại của lượt đi hiện tại.
        """
        if self.state == "MENU":
            if BG_MAIN: screen.blit(BG_MAIN, (0, 0))
            else: screen.fill(BLACK)
            self.play_btn.draw(screen)

        elif self.state == "MODE_SELECT":
            if BG_SELECT: screen.blit(BG_SELECT, (0, 0))
            else: screen.fill(BLACK)
            self.pvp_btn.draw(screen)
            self.pva_btn.draw(screen)

        elif self.state == "PLAYING":
            if BG_PLAY: screen.blit(BG_PLAY, (0, 0))
            else: screen.fill(WHITE)

            for i in range(self.board_size + 1):
                pos_h_start = (self.board_x, self.board_y + i * self.square_size)
                pos_h_end = (self.board_x + self.board_width, self.board_y + i * self.square_size)
                pygame.draw.line(screen, GRID_COLOR, pos_h_start, pos_h_end, 1)

                pos_v_start = (self.board_x + i * self.square_size, self.board_y)
                pos_v_end = (self.board_x + i * self.square_size, self.board_y + self.board_width)
                pygame.draw.line(screen, GRID_COLOR, pos_v_start, pos_v_end, 1)

            for r in range(self.board_size):
                for c in range(self.board_size):
                    if self.board[r][c] == "X": self.draw_x(screen, r, c)
                    elif self.board[r][c] == "O": self.draw_o(screen, r, c)

            time_str = f"{int(time_left)}s"
            time_surf = font_huge.render(time_str, True, BLACK)
            time_rect = time_surf.get_rect(center=(1040, 235))
            screen.blit(time_surf, time_rect)  

            turn_color = RED if self.current_player == "X" else BLUE
            turn_surf = font_huge.render(self.current_player, True, turn_color)
            turn_rect = turn_surf.get_rect(center=(1050, 535))
            screen.blit(turn_surf, turn_rect)  

            self.reset_btn.draw(screen)

            if self.game_over:
                screen.blit(DARK_OVERLAY, (0, 0))
                
                current_popup = None
                
                if self.game_mode == "PvP":
                    if self.winner == "X": current_popup = POPUP_PVP_X
                    elif self.winner == "O": current_popup = POPUP_PVP_O
                    elif self.winner == "DRAW": current_popup = POPUP_DRAW
                        
                elif self.game_mode == "PvAI":
                    if self.winner == "X": current_popup = POPUP_PVA_WIN
                    elif self.winner == "O": current_popup = POPUP_PVA_LOSE
                    elif self.winner == "DRAW": current_popup = POPUP_DRAW

                if current_popup:
                    popup_rect = current_popup.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                    screen.blit(current_popup, popup_rect)

                self.play_again_btn.draw(screen)

def main():
    """
    Hàm thực thi chính của trò chơi (Game Loop).
    Xử lý thời gian thực, sự kiện chuột/bàn phím và tương tác giữa người với AI.
    """

    game = CaroGame()
    ai = CaroAI()
    clock = pygame.time.Clock()
    running = True

    while running:
        time_left = 0
        if game.state == "PLAYING":
            curr_time = pygame.time.get_ticks()
            seconds_passed = (curr_time - game.start_ticks) / 1000
            time_left = max(0, game.time_limit - seconds_passed)
            
            if time_left == 0 and not game.game_over:
                game.current_player = "O" if game.current_player == "X" else "X"
                game.start_ticks = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if game.state == "MENU":
                if game.play_btn.handle_event(event):
                    game.state = "MODE_SELECT"

            elif game.state == "MODE_SELECT":
                if game.pvp_btn.handle_event(event):
                    game.reset_game()
                    game.game_mode = "PvP"
                    game.state = "PLAYING"
                if game.pva_btn.handle_event(event):
                    game.reset_game()
                    game.game_mode = "PvAI"
                    game.state = "PLAYING"

            elif game.state == "PLAYING":
                if game.reset_btn.handle_event(event):
                    game.state = "MENU"
                
                if game.game_over:
                    if game.play_again_btn.handle_event(event):
                        current_mode = game.game_mode  
                        game.reset_game()
                        game.game_mode = current_mode
                
                elif event.type == pygame.MOUSEBUTTONDOWN and not game.game_over:
                    mx, my = pygame.mouse.get_pos()
                    
                    if game.board_x <= mx < game.board_x + game.board_width and \
                       game.board_y <= my < game.board_y + game.board_width:
                        
                        col = (mx - game.board_x) // game.square_size
                        row = (my - game.board_y) // game.square_size
                        
                        if 0 <= row < game.board_size and 0 <= col < game.board_size and game.board[row][col] == "":
                            game.board[row][col] = game.current_player
                            if game.check_win(row, col):
                                game.winner = game.current_player
                                game.game_over = True
                            else:
                                game.current_player = "O" if game.current_player == "X" else "X"
                                game.start_ticks = pygame.time.get_ticks()

        if game.state == "PLAYING" and not game.game_over and game.game_mode == "PvAI" and game.current_player == "O":
            best_move = ai.best_moves(game.board)
            if best_move:
                r, c = best_move
                game.board[r][c] = "O"
                if game.check_win(r, c): 
                    game.winner = "O"
                    game.game_over = True
                else:
                    game.current_player = "X"
                    game.start_ticks = pygame.time.get_ticks()

        game.draw_screens(screen, time_left)
        pygame.display.update()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()