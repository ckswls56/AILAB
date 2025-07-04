"""
게임 클래스
오목 게임의 메인 로직과 상태 관리를 담당합니다.
"""

import pygame
from typing import Optional, Tuple
from board import Board
from renderer import Renderer
from ai import AI
from utils import screen_to_board_pos


class Game:
    """오목 게임 메인 클래스"""
    
    def __init__(self, screen_width: int = 800, screen_height: int = 600):
        """
        게임 초기화
        
        Args:
            screen_width (int): 화면 너비
            screen_height (int): 화면 높이
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Pygame 초기화
        pygame.init()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("3D Gomoku Game")
        
        # 게임 컴포넌트 초기화
        self.board = Board()
        self.renderer = Renderer(screen_width, screen_height)
        self.ai = AI(player=2)  # AI는 백돌
        
        # 게임 상태
        self.game_mode = "2-Player"  # "2-Player" 또는 "AI Battle"
        self.running = True
        self.clock = pygame.time.Clock()
        
        # 로딩 화면 표시
        self.show_loading_screen()
    
    def show_loading_screen(self):
        """로딩 화면 표시"""
        for i in range(101):
            self.renderer.render_loading_screen(self.screen, i / 100)
            pygame.display.flip()
            pygame.time.wait(20)
    
    def handle_events(self):
        """이벤트 처리"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event.key)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 왼쪽 클릭
                    self.handle_mouse_click(event.pos)
    
    def handle_keydown(self, key):
        """키보드 이벤트 처리"""
        if key == pygame.K_ESCAPE:
            self.running = False
        elif key == pygame.K_r:
            self.restart_game()
        elif key == pygame.K_1:
            self.set_game_mode("2-Player")
        elif key == pygame.K_2:
            self.set_game_mode("AI Battle")
    
    def handle_mouse_click(self, pos):
        """마우스 클릭 처리"""
        # 보드 영역 확인
        board_rect = self.renderer.get_board_rect()
        cell_size = self.renderer.get_cell_size()
        
        board_pos = screen_to_board_pos(pos, board_rect, cell_size)
        
        if board_pos:
            row, col = board_pos
            if self.board.place_stone(row, col):
                # AI 대전 모드에서 AI 차례 처리
                if self.game_mode == "AI Battle" and not self.board.game_over:
                    self.handle_ai_turn()
    
    def handle_ai_turn(self):
        """AI 차례 처리"""
        if self.board.get_current_player() == self.ai.player:
            # AI 수 계산
            ai_move = self.ai.get_move(self.board)
            
            if ai_move:
                row, col = ai_move
                self.board.place_stone(row, col)
    
    def set_game_mode(self, mode: str):
        """
        게임 모드 설정
        
        Args:
            mode (str): 게임 모드 ("2-Player" 또는 "AI Battle")
        """
        self.game_mode = mode
        self.restart_game()
    
    def restart_game(self):
        """게임 재시작"""
        self.board.reset()
    
    def update(self):
        """게임 상태 업데이트"""
        # 게임 종료 조건 확인
        game_over, winner = self.board.get_game_status()
        
        if game_over:
            # 게임 종료 시 잠시 대기
            pygame.time.wait(2000)
            self.restart_game()
    
    def render(self):
        """게임 렌더링"""
        # 배경 그리기
        self.screen.fill(self.renderer.colors['background'])
        
        # 보드 렌더링
        self.renderer.render_board(self.screen, self.board)
        
        # UI 렌더링
        self.renderer.render_ui(self.screen, self.board, self.game_mode)
        
        # 화면 업데이트
        pygame.display.flip()
    
    def run(self):
        """게임 메인 루프"""
        while self.running:
            # 이벤트 처리
            self.handle_events()
            
            # 게임 상태 업데이트
            self.update()
            
            # 렌더링
            self.render()
            
            # FPS 제한
            self.clock.tick(60)
        
        # 게임 종료
        pygame.quit()
    
    def get_game_state(self):
        """
        현재 게임 상태 반환
        
        Returns:
            dict: 게임 상태 정보
        """
        game_over, winner = self.board.get_game_status()
        return {
            'game_mode': self.game_mode,
            'current_player': self.board.get_current_player(),
            'game_over': game_over,
            'winner': winner,
            'board_state': self.board.get_board_state().tolist()
        } 