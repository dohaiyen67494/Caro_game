"""
Trí tuệ nhân tạo (AI) chơi game Caro.

Sử dụng thuật toán Minimax kết hợp cắt tỉa Alpha - Beta và hàm đánh giá Heuristic 
dựa trên việc nhận diện chuỗi cờ (Pattern Matching).

Attributes:
    ai_player: kí hiệu quân cờ của AI (quy định là "O").
    human_player: kí hiệu quân cờ của người chơi (quy định là "X").

"""
BOARD_SIZE = 15

class CaroAI:
    def __init__(self, ai_player="O", human_player="X"):
        self.ai_player = ai_player
        self.human_player = human_player
    
    def get_line_score(self, count, blocks):
        """
        Chấm điểm cho một chuối quân cờ dựa trên độ dài và số đầu bị chặn.

        Args:
            count: số lượng quân cờ liên tiếp trong chuỗi.
            blocks: số đầu bị dối phương chặn.
        
        Returns:
            Điểm số của chuỗi. Điểm số càng cao khi chuỗi càng dài và ít bị chặn.
            Trả về 0 nếu chuỗi bị chặn 2 đầu (trừ trường hợp đủ 5 quân).
        
        """
        if blocks == 2 and count < 5: 
            return 0
        if count >= 5: return 100000
        elif count == 4:
            return 10000 if blocks == 0 else 1000
        elif count == 3:
            return 1000 if blocks == 0 else 100
        elif count == 2:
            return 100 if blocks == 0 else 10
        elif count == 1:
            return 10 if blocks == 0 else 1
        return 0

    def evaluate_position(self, board, r, c, player):
        """
        Tính điểm của một ô cụ thể nếu đặt quân cờ vào.

        Quét 4 hướng (ngang, dọc, 2 chéo) tính từ ô (r, c) và đếm chuỗi quân cờ hiện có, 
        sau đó cộng điểm lại.

        Args:
            board: ma trận 2D đại diện cho trạng thái bàn cờ.
            r: chỉ số dòng (row) của ô cần đánh giá.
            c: chỉ số cột (column) của ô cần đánh giá.
            player: quân cờ cần tính điểm ("X" hoặc "O").
        
        Returns:
            Số điểm của ô đó.
        
        """
        score = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        opponent = self.human_player if player == self.ai_player else self.ai_player

        for dr, dc in directions:
            count = 1
            blocks = 0
            for i in range(1, 5):
                nr, nc = r + dr*i, c + dc*i
                if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                    if board[nr][nc] == player: count += 1
                    elif board[nr][nc] == opponent:
                        blocks += 1
                        break
                    else: break
                else:
                    blocks += 1
                    break
            
            for i in range(1, 5):
                nr, nc = r - dr*i, c - dc*i
                if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                    if board[nr][nc] == player: count += 1
                    elif board[nr][nc] == opponent:
                        blocks += 1
                        break
                    else: break
                else:
                    blocks += 1
                    break
            
            score += self.get_line_score(count, blocks)
        return score
    
    def get_candidates_move(self, board):

        moves = set()
        has_piece = False
        
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if board[r][c] != "":
                    has_piece = True
                    for dr in [-2, -1, 0, 1, 2]:
                        for dc in [-2, -1, 0, 1, 2]:
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and board[nr][nc] == "":
                                moves.add((nr, nc))
        
        if not has_piece: return [(BOARD_SIZE//2, BOARD_SIZE//2)]
        candidates = list(moves)
        candidates.sort(key=lambda m: self.evaluate_position(board, m[0], m[1], self.ai_player) + 
                                      self.evaluate_position(board, m[0], m[1], self.human_player), reverse=True)
        return candidates[:15]

    def check_win(self, board, r, c):
        player = board[r][c]
        if player == "": return False
        for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1)]:
            count = 1
            for i in range(1, 5):
                nr, nc = r + dr*i, c + dc*i
                if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and board[nr][nc] == player: count += 1
                else: break
            for i in range(1, 5):
                nr, nc = r - dr*i, c - dc*i
                if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and board[nr][nc] == player: count += 1
                else: break
            if count >= 5: return True
        return False
    
    def evaluate_board_state(self, board):
        ai_score = 0
        human_score = 0
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if board[r][c] == self.ai_player:
                    ai_score += self.evaluate_position(board, r, c, self.ai_player)
                elif board[r][c] == self.human_player:
                    human_score += self.evaluate_position(board, r, c, self.human_player)
        return ai_score - human_score

    def minimax(self, board, depth, alpha, beta, is_max):
        """
        Thuật toán Minimax duyệt cây để tìm nước đi tối ưu.

        Args:
            board: Trạng thái bàn cờ hiện tại.
            depth: Độ sâu giới hạn của cây tìm kiếm (số nước đi dự đoán trước).
            alpha: Giá trị tốt nhất cho Node Max.
            beta: Giá trị tốt nhất cho Node Min.
            bool is_max: True nếu đang ở lượt chơi của AI ("O"), False nếu đang ở lượt đi của người ("X").
        
        Returns:
            Trả về điểm số Heuristic đánh giá trạng thái bàn cờ tại Node lá.
        """
        if depth == 0:
            return self.evaluate_board_state(board)
        
        candidates = self.get_candidates_move(board)
        if not candidates: return 0

        if is_max:
            best_score = -float("inf")
            for r, c in candidates:
                board[r][c] = self.ai_player
                if self.check_win(board, r, c): 
                    score = 100000 + depth
                else:
                    score = self.minimax(board, depth - 1, alpha, beta, False)
                board[r][c] = ""
                
                best_score = max(score, best_score)
                alpha = max(alpha, best_score)
                if beta <= alpha: break
            return best_score
        else:
            best_score = float("inf")
            for r, c in candidates:
                board[r][c] = self.human_player
                if self.check_win(board, r, c):
                    score = -100000 - depth
                else:
                    score = self.minimax(board, depth - 1, alpha, beta, True)
                board[r][c] = ""
                
                best_score = min(score, best_score)
                beta = min(beta, best_score)
                if beta <= alpha: break
            return best_score

    def best_moves(self, board):
        """
        Tìm nước đi tốt nhất cho AI trên bàn cờ hiện tại.

        Lọc ra những nước đi tiềm năng nhất và sử dụng Minimax để dự đoán.
        Nếu bàn cờ trống, ưu tiên đánh thẳng vào chính giữa bàn cờ.

        Args:
            board: Trạng thái bàn cờ hiện tại.
        
        Returns:
            Tọa độ (dòng, cột) của nước đi tốt nhất cho AI.
        """
        candidates = self.get_candidates_move(board)
        if not candidates: return (BOARD_SIZE//2, BOARD_SIZE//2)

        best_val = -float("inf")
        alpha = -float("inf")
        beta = float("inf")
        best_move = candidates[0]

        for r, c in candidates:
            board[r][c] = self.ai_player
            if self.check_win(board, r, c):
                board[r][c] = ""
                return (r, c)
            
            m_val = self.minimax(board, 2, alpha, beta, False) 
            board[r][c] = ""
            
            if m_val > best_val:
                best_val = m_val
                best_move = (r, c)
            
            alpha = max(alpha, best_val) 

        return best_move