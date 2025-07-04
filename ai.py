"""
AI 클래스
오목 게임을 위한 간단한 AI 알고리즘을 구현합니다.
"""

import random
from typing import Tuple, List, Optional
from board import Board


class AI:
    """오목 AI 클래스 - 미니맥스 알고리즘과 알파베타 가지치기 사용"""
    
    def __init__(self, player: int, depth: int = 3):
        """
        AI 초기화
        
        Args:
            player (int): AI 플레이어 번호 (1: 흑돌, 2: 백돌)
            depth (int): 탐색 깊이
        """
        self.player = player
        self.opponent = 3 - player  # 상대방 플레이어
        self.depth = depth
        
        # 위치별 가중치 (중앙일수록 높은 가중치)
        self.position_weights = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 2, 2, 2, 2, 2, 2, 1, 0],
            [0, 1, 2, 3, 3, 3, 3, 2, 1, 0],
            [0, 1, 2, 3, 4, 4, 3, 2, 1, 0],
            [0, 1, 2, 3, 4, 4, 3, 2, 1, 0],
            [0, 1, 2, 3, 3, 3, 3, 2, 1, 0],
            [0, 1, 2, 2, 2, 2, 2, 2, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ]
    
    def get_move(self, board: Board) -> Tuple[int, int]:
        """
        AI의 다음 수를 결정
        
        Args:
            board (Board): 현재 게임 보드
            
        Returns:
            Tuple[int, int]: 선택한 위치 (row, col)
        """
        valid_moves = board.get_valid_moves()
        
        if not valid_moves:
            return None
        
        # 첫 번째 수는 중앙에
        if len(valid_moves) == 100:  # 빈 보드
            return (4, 4)
        
        # 미니맥스 알고리즘으로 최적의 수 찾기
        best_move = None
        best_score = float('-inf')
        
        for move in valid_moves:
            # 임시로 수를 두고 평가
            row, col = move
            board.board[row, col] = self.player
            
            score = self.minimax(board, self.depth - 1, False, float('-inf'), float('inf'))
            
            # 수를 되돌리기
            board.board[row, col] = 0
            
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move
    
    def minimax(self, board: Board, depth: int, is_maximizing: bool, 
                alpha: float, beta: float) -> float:
        """
        미니맥스 알고리즘 (알파베타 가지치기 포함)
        
        Args:
            board (Board): 게임 보드
            depth (int): 탐색 깊이
            is_maximizing (bool): 최대화 플레이어인지 여부
            alpha (float): 알파 값
            beta (float): 베타 값
            
        Returns:
            float: 평가 점수
        """
        # 종료 조건
        game_over, winner = board.get_game_status()
        if game_over or depth == 0:
            return self.evaluate_board(board)
        
        valid_moves = board.get_valid_moves()
        
        if is_maximizing:
            max_score = float('-inf')
            for move in valid_moves:
                row, col = move
                board.board[row, col] = self.player
                
                score = self.minimax(board, depth - 1, False, alpha, beta)
                
                board.board[row, col] = 0
                
                max_score = max(max_score, score)
                alpha = max(alpha, score)
                
                if beta <= alpha:
                    break
            
            return max_score
        else:
            min_score = float('inf')
            for move in valid_moves:
                row, col = move
                board.board[row, col] = self.opponent
                
                score = self.minimax(board, depth - 1, True, alpha, beta)
                
                board.board[row, col] = 0
                
                min_score = min(min_score, score)
                beta = min(beta, score)
                
                if beta <= alpha:
                    break
            
            return min_score
    
    def evaluate_board(self, board: Board) -> float:
        """
        보드 상태 평가
        
        Args:
            board (Board): 평가할 보드
            
        Returns:
            float: 평가 점수
        """
        score = 0
        board_state = board.get_board_state()
        
        # 승리 조건 확인
        game_over, winner = board.get_game_status()
        if game_over:
            if winner == self.player:
                return 10000  # AI 승리
            elif winner == self.opponent:
                return -10000  # AI 패배
            else:
                return 0  # 무승부
        
        # 각 위치별 평가
        for row in range(board.size):
            for col in range(board.size):
                if board_state[row, col] != 0:
                    player = board_state[row, col]
                    weight = self.position_weights[row][col]
                    
                    # 연속된 돌 개수 계산
                    consecutive = self.count_consecutive(board_state, row, col, player)
                    
                    if player == self.player:
                        score += consecutive * weight * 10
                    else:
                        score -= consecutive * weight * 10
        
        return score
    
    def count_consecutive(self, board_state, row: int, col: int, player: int) -> int:
        """
        특정 위치에서 연속된 돌 개수 계산
        
        Args:
            board_state: 보드 상태
            row (int): 행 인덱스
            col (int): 열 인덱스
            player (int): 플레이어 번호
            
        Returns:
            int: 연속된 돌 개수
        """
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        max_consecutive = 0
        
        for dr, dc in directions:
            count = 1  # 현재 위치 포함
            
            # 정방향
            r, c = row + dr, col + dc
            while 0 <= r < len(board_state) and 0 <= c < len(board_state[0]) and board_state[r, c] == player:
                count += 1
                r += dr
                c += dc
            
            # 역방향
            r, c = row - dr, col - dc
            while 0 <= r < len(board_state) and 0 <= c < len(board_state[0]) and board_state[r, c] == player:
                count += 1
                r -= dr
                c -= dc
            
            max_consecutive = max(max_consecutive, count)
        
        return max_consecutive
    
    def get_random_move(self, board: Board) -> Tuple[int, int]:
        """
        랜덤한 수 선택 (간단한 AI)
        
        Args:
            board (Board): 게임 보드
            
        Returns:
            Tuple[int, int]: 선택한 위치
        """
        valid_moves = board.get_valid_moves()
        if valid_moves:
            return random.choice(valid_moves)
        return None 