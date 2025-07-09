"""
오목판 클래스
오목 게임의 보드 상태를 관리하고 승리 조건을 확인합니다.
"""

import numpy as np
from typing import Tuple, Optional, List


class Board:
    """오목판 클래스 - 게임 상태와 승리 조건을 관리"""
    
    def __init__(self, size: int = 10):
        """
        오목판 초기화
        
        Args:
            size (int): 보드 크기 (기본값: 10x10)
        """
        self.size = size
        # 0: 빈 칸, 1: 흑돌, 2: 백돌
        self.board = np.zeros((size, size), dtype=int)
        self.current_player = 1  # 1: 흑돌, 2: 백돌
        self.game_over = False
        self.winner = None
        self.last_move = None
        
    def reset(self):
        """게임 보드를 초기 상태로 리셋"""
        self.board = np.zeros((self.size, self.size), dtype=int)
        self.current_player = 1
        self.game_over = False
        self.winner = None
        self.last_move = None
        
    def is_valid_move(self, row: int, col: int) -> bool:
        """
        주어진 위치에 돌을 놓을 수 있는지 확인
        
        Args:
            row (int): 행 인덱스
            col (int): 열 인덱스
            
        Returns:
            bool: 유효한 이동인지 여부
        """
        # 보드 범위 확인
        if not (0 <= row < self.size and 0 <= col < self.size):
            return False
        
        # 이미 돌이 놓여있는지 확인
        if self.board[row, col] != 0:
            return False
            
        return True
    
    def place_stone(self, row: int, col: int) -> bool:
        """
        주어진 위치에 돌을 놓기
        
        Args:
            row (int): 행 인덱스
            col (int): 열 인덱스
            
        Returns:
            bool: 돌을 놓았는지 여부
        """
        if not self.is_valid_move(row, col):
            return False
            
        self.board[row, col] = self.current_player
        self.last_move = (row, col)
        
        # 승리 조건 확인
        if self.check_win(row, col):
            self.game_over = True
            self.winner = self.current_player
        else:
            # 플레이어 변경
            self.current_player = 3 - self.current_player  # 1 -> 2, 2 -> 1
            
        return True
    
    def check_win(self, row: int, col: int) -> bool:
        """
        마지막으로 놓은 돌을 기준으로 승리 조건 확인 (최적화된 버전)
        
        Args:
            row (int): 마지막 돌의 행 인덱스
            col (int): 마지막 돌의 열 인덱스
            
        Returns:
            bool: 승리 여부
        """
        player = self.board[row, col]
        
        # 확인할 방향들 (가로, 세로, 대각선)
        directions = [
            (0, 1),   # 가로
            (1, 0),   # 세로
            (1, 1),   # 우하향 대각선
            (1, -1)   # 좌하향 대각선
        ]
        
        for dr, dc in directions:
            count = 1  # 현재 위치 포함
            
            # 양방향으로 확인 (최적화된 방식)
            # 정방향
            r, c = row + dr, col + dc
            while (0 <= r < self.size and 0 <= c < self.size and 
                   self.board[r, c] == player):
                count += 1
                r += dr
                c += dc
                # 5개 이상이면 즉시 반환
                if count >= 5:
                    return True
            
            # 역방향
            r, c = row - dr, col - dc
            while (0 <= r < self.size and 0 <= c < self.size and 
                   self.board[r, c] == player):
                count += 1
                r -= dr
                c -= dc
                # 5개 이상이면 즉시 반환
                if count >= 5:
                    return True
            
            # 이미 5개 이상이면 즉시 반환
            if count >= 5:
                return True
                
        return False
    
    def check_win_optimized(self, row: int, col: int) -> bool:
        """
        더욱 최적화된 승리 조건 확인 (경계 체크 최적화)
        
        Args:
            row (int): 마지막 돌의 행 인덱스
            col (int): 마지막 돌의 열 인덱스
            
        Returns:
            bool: 승리 여부
        """
        player = self.board[row, col]
        size = self.size
        
        # 각 방향별로 최대 가능한 연속 돌 개수 계산
        directions = [
            (0, 1, min(5, size - col), min(5, col + 1)),      # 가로
            (1, 0, min(5, size - row), min(5, row + 1)),      # 세로
            (1, 1, min(5, size - max(row, col)), min(5, min(row, col) + 1)),  # 우하향 대각선
            (1, -1, min(5, size - row), min(5, size - col))   # 좌하향 대각선
        ]
        
        for dr, dc, max_forward, max_backward in directions:
            # 최대 가능한 연속 돌 개수가 5개 미만이면 건너뛰기
            if max_forward + max_backward - 1 < 5:
                continue
                
            count = 1
            
            # 정방향 확인
            for i in range(1, max_forward):
                r, c = row + i * dr, col + i * dc
                if self.board[r, c] != player:
                    break
                count += 1
                if count >= 5:
                    return True
            
            # 역방향 확인
            for i in range(1, max_backward):
                r, c = row - i * dr, col - i * dc
                if self.board[r, c] != player:
                    break
                count += 1
                if count >= 5:
                    return True
                    
        return False
    
    def get_valid_moves(self) -> List[Tuple[int, int]]:
        """
        현재 보드에서 가능한 모든 이동 위치 반환
        
        Returns:
            List[Tuple[int, int]]: 가능한 이동 위치들의 리스트
        """
        valid_moves = []
        for row in range(self.size):
            for col in range(self.size):
                if self.is_valid_move(row, col):
                    valid_moves.append((row, col))
        return valid_moves
    
    def is_full(self) -> bool:
        """
        보드가 가득 찼는지 확인
        
        Returns:
            bool: 보드가 가득 찬 여부
        """
        return bool(np.all(self.board != 0))
    
    def check_draw(self) -> bool:
        """
        무승부 조건 확인 (보드가 가득 찬 경우)
        
        Returns:
            bool: 무승부 여부
        """
        return self.is_full()
    
    def get_game_result(self) -> tuple[bool, Optional[int], bool]:
        """
        게임 결과 반환 (게임 종료, 승자, 무승부)
        
        Returns:
            tuple: (게임 종료 여부, 승자, 무승부 여부)
        """
        if self.game_over:
            if self.winner:
                return True, self.winner, False  # 승자가 있음
            else:
                return True, None, True  # 무승부
        elif self.is_full():
            return True, None, True  # 보드가 가득 참 (무승부)
        else:
            return False, None, False  # 게임 계속
    
    def get_board_state(self) -> np.ndarray:
        """
        현재 보드 상태 반환
        
        Returns:
            np.ndarray: 현재 보드 상태
        """
        return self.board.copy()
    
    def get_current_player(self) -> int:
        """
        현재 플레이어 반환
        
        Returns:
            int: 현재 플레이어 (1: 흑돌, 2: 백돌)
        """
        return self.current_player
    
    def get_game_status(self) -> Tuple[bool, Optional[int]]:
        """
        게임 상태 반환
        
        Returns:
            Tuple[bool, Optional[int]]: (게임 종료 여부, 승자)
        """
        return self.game_over, self.winner 