"""
AI 클래스
오목 게임을 위한 고성능 AI 알고리즘을 구현합니다.
"""

import random
import time
import numpy as np
from typing import Tuple, List, Optional
from board import Board


class AI:
    """오목 AI 클래스 - 미니맥스 알고리즘과 알파베타 가지치기 사용"""
    
    def __init__(self, player: int, difficulty: str = "Medium"):
        """
        AI 초기화
        
        Args:
            player (int): AI 플레이어 번호 (1: 흑돌, 2: 백돌)
            difficulty (str): AI 난이도 ("Easy", "Medium", "Hard", "Expert")
        """
        self.player = player
        self.opponent = 3 - player  # 상대방 플레이어
        self.difficulty = difficulty
        
        # 난이도별 설정 (극한 성능 최적화)
        self.difficulty_settings = {
            "Easy": {"depth": 1, "random_factor": 0.9, "use_minimax": False, "max_moves": 8},
            "Medium": {"depth": 2, "random_factor": 0.6, "use_minimax": True, "max_moves": 6},
            "Hard": {"depth": 2, "random_factor": 0.4, "use_minimax": True, "max_moves": 4},
            "Expert": {"depth": 2, "random_factor": 0.2, "use_minimax": True, "max_moves": 3}
        }
        
        self.settings = self.difficulty_settings.get(difficulty, self.difficulty_settings["Medium"])
        self.depth = self.settings["depth"]
        
        # 캐싱 시스템 (성능 향상)
        self.evaluation_cache = {}
        self.move_cache = {}
        
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
    
    def set_difficulty(self, difficulty: str):
        """
        AI 난이도 설정
        
        Args:
            difficulty (str): 난이도 ("Easy", "Medium", "Hard", "Expert")
        """
        if difficulty in self.difficulty_settings:
            self.difficulty = difficulty
            self.settings = self.difficulty_settings[difficulty]
            self.depth = self.settings["depth"]
            # 난이도 변경 시 캐시 정리
            self.clear_cache()
    
    def clear_cache(self):
        """캐시 정리 (메모리 관리)"""
        self.evaluation_cache.clear()
        self.move_cache.clear()
    
    def get_move(self, board: Board) -> Optional[Tuple[int, int]]:
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
        
        # 난이도에 따른 랜덤 요소 적용
        if random.random() < self.settings["random_factor"]:
            return self.get_random_move(board)
        
        # 미니맥스 알고리즘 사용 여부
        if not self.settings["use_minimax"]:
            return self.get_simple_move(board)
        
        # 스마트한 수 선택 (중요한 수만 고려)
        smart_moves = self.get_smart_moves(board, valid_moves)
        
        # 미니맥스 알고리즘으로 최적의 수 찾기
        best_move = None
        best_score = float('-inf')
        
        for move in smart_moves:
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
        미니맥스 알고리즘 (극한 성능 최적화)
        
        Args:
            board (Board): 게임 보드
            depth (int): 탐색 깊이
            is_maximizing (bool): 최대화 플레이어인지 여부
            alpha (float): 알파 값
            beta (float): 베타 값
            
        Returns:
            float: 평가 점수
        """
        # 시간 제한 확인 (0.3초) - 제거하여 성능 향상
        # if hasattr(self, 'start_time') and time.time() - self.start_time > 0.3:
        #     return 0
        
        # 종료 조건
        game_over, winner = board.get_game_status()
        if game_over or depth == 0:
            return self.evaluate_board(board)
        
        valid_moves = board.get_valid_moves()
        
        # 더 적은 수만 고려 (극한 최적화)
        if len(valid_moves) > 3:
            # 우선순위가 높은 수만 선택
            priority_moves = []
            for move in valid_moves:
                row, col = move
                priority = self.get_move_priority(board, row, col)
                priority_moves.append((move, priority))
            
            priority_moves.sort(key=lambda x: x[1], reverse=True)
            smart_moves = [move for move, _ in priority_moves[:3]]
        else:
            smart_moves = valid_moves
        
        if is_maximizing:
            max_score = float('-inf')
            for move in smart_moves:
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
            for move in smart_moves:
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
        고성능 보드 상태 평가 (캐싱 및 벡터화 연산 사용)
        
        Args:
            board (Board): 평가할 보드
            
        Returns:
            float: 평가 점수
        """
        # 보드 상태를 문자열로 변환하여 캐시 키 생성
        board_state = board.get_board_state()
        cache_key = board_state.tobytes()
        
        # 캐시에서 확인
        if cache_key in self.evaluation_cache:
            return self.evaluation_cache[cache_key]
        
        # 승리 조건 확인 (빠른 체크)
        game_over, winner = board.get_game_status()
        if game_over:
            if winner == self.player:
                result = 10000
            elif winner == self.opponent:
                result = -10000
            else:
                result = 0
            self.evaluation_cache[cache_key] = result
            return result
        
        # 벡터화된 평가 (NumPy 사용)
        score = self.evaluate_board_fast(board_state)
        
        # 캐시에 저장
        self.evaluation_cache[cache_key] = score
        return score
    
    def evaluate_board_fast(self, board_state: np.ndarray) -> float:
        """
        NumPy를 사용한 고성능 보드 평가
        
        Args:
            board_state (np.ndarray): 보드 상태
            
        Returns:
            float: 평가 점수
        """
        score = 0.0
        
        # 플레이어별 마스크 생성
        player_mask = (board_state == self.player).astype(int)
        opponent_mask = (board_state == self.opponent).astype(int)
        
        # 가중치 행렬 적용
        weights = np.array(self.position_weights)
        
        # 각 방향별로 연속된 돌 계산
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for dr, dc in directions:
            # 플레이어 돌의 연속성 계산
            player_score = self.count_consecutive_fast(board_state, self.player, dr, dc)
            opponent_score = self.count_consecutive_fast(board_state, self.opponent, dr, dc)
            
            score += player_score * 10
            score -= opponent_score * 10
        
        return score
    
    def count_consecutive_fast(self, board_state: np.ndarray, player: int, dr: int, dc: int) -> float:
        """
        NumPy를 사용한 고성능 연속 돌 계산
        
        Args:
            board_state (np.ndarray): 보드 상태
            player (int): 플레이어 번호
            dr (int): 행 방향
            dc (int): 열 방향
            
        Returns:
            float: 연속된 돌 점수
        """
        size = board_state.shape[0]
        max_consecutive = 0
        
        # 각 시작점에서 연속성 확인
        for start_row in range(size):
            for start_col in range(size):
                if board_state[start_row, start_col] == player:
                    count = 1
                    r, c = start_row + dr, start_col + dc
                    
                    # 정방향으로 연속된 돌 개수 확인
                    while 0 <= r < size and 0 <= c < size and board_state[r, c] == player:
                        count += 1
                        r += dr
                        c += dc
                    
                    max_consecutive = max(max_consecutive, count)
        
        return max_consecutive
    
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
    
    def get_random_move(self, board: Board) -> Optional[Tuple[int, int]]:
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

    def get_simple_move(self, board: Board) -> Optional[Tuple[int, int]]:
        """
        간단한 AI 수 선택 (난이도 Easy용)
        
        Args:
            board (Board): 게임 보드
            
        Returns:
            Tuple[int, int]: 선택한 위치
        """
        valid_moves = board.get_valid_moves()
        if not valid_moves:
            return None
        
        # 공격 기회가 있는지 확인
        for move in valid_moves:
            row, col = move
            board.board[row, col] = self.player
            if board.check_win(row, col):
                board.board[row, col] = 0
                return move
            board.board[row, col] = 0
        
        # 방어 기회가 있는지 확인
        for move in valid_moves:
            row, col = move
            board.board[row, col] = self.opponent
            if board.check_win(row, col):
                board.board[row, col] = 0
                return move
            board.board[row, col] = 0
        
        # 중앙 근처 우선 선택
        center_moves = [(4, 4), (4, 5), (5, 4), (5, 5), (3, 4), (4, 3), (6, 4), (4, 6)]
        for move in center_moves:
            if move in valid_moves:
                return move
        
        # 랜덤 선택
        return random.choice(valid_moves)
    
    def get_smart_moves(self, board: Board, valid_moves: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """
        스마트한 수 선택 (중요한 수만 고려하여 성능 향상)
        
        Args:
            board (Board): 게임 보드
            valid_moves (List[Tuple[int, int]]): 가능한 모든 수
            
        Returns:
            List[Tuple[int, int]]: 고려할 중요한 수들
        """
        if len(valid_moves) <= self.settings["max_moves"]:
            return valid_moves
        
        # 우선순위별로 수를 분류
        priority_moves = []
        normal_moves = []
        
        for move in valid_moves:
            row, col = move
            priority = self.get_move_priority(board, row, col)
            
            if priority > 0:
                priority_moves.append((move, priority))
            else:
                normal_moves.append(move)
        
        # 우선순위가 높은 수들을 우선 선택
        priority_moves.sort(key=lambda x: x[1], reverse=True)
        selected_moves = [move for move, _ in priority_moves]
        
        # 남은 자리를 일반 수로 채움
        remaining_slots = self.settings["max_moves"] - len(selected_moves)
        if remaining_slots > 0 and normal_moves:
            selected_moves.extend(random.sample(normal_moves, min(remaining_slots, len(normal_moves))))
        
        return selected_moves
    
    def get_move_priority(self, board: Board, row: int, col: int) -> int:
        """
        수의 우선순위 계산
        
        Args:
            board (Board): 게임 보드
            row (int): 행 인덱스
            col (int): 열 인덱스
            
        Returns:
            int: 우선순위 점수 (높을수록 중요)
        """
        priority = 0
        board_state = board.get_board_state()
        
        # 승리 기회 확인
        board.board[row, col] = self.player
        if board.check_win(row, col):
            priority += 1000
        board.board[row, col] = 0
        
        # 방어 기회 확인
        board.board[row, col] = self.opponent
        if board.check_win(row, col):
            priority += 800
        board.board[row, col] = 0
        
        # 기존 돌 근처인지 확인
        for dr in range(-2, 3):
            for dc in range(-2, 3):
                r, c = row + dr, col + dc
                if 0 <= r < board.size and 0 <= c < board.size and board_state[r, c] != 0:
                    priority += 10
                    # 더 가까울수록 높은 점수
                    distance = abs(dr) + abs(dc)
                    priority += (3 - distance) * 5
        
        # 중앙 근처인지 확인
        center_distance = abs(row - 4.5) + abs(col - 4.5)
        priority += max(0, 10 - int(center_distance))
        
        return priority 