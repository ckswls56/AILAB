"""
3D 렌더링 클래스
게임의 3D 시각 효과와 렌더링을 담당합니다.
"""

import pygame
from typing import Tuple, Optional
from board import Board
from utils import create_3d_effect, draw_text_with_shadow, board_to_screen_pos


class Renderer:
    """3D 오목 게임 렌더링 클래스"""
    
    def __init__(self, screen_width: int = 800, screen_height: int = 600):
        """
        렌더러 초기화
        
        Args:
            screen_width (int): 화면 너비
            screen_height (int): 화면 높이
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # 색상 정의
        self.colors = {
            'background': (34, 139, 34),      # 포레스트 그린
            'board': (205, 133, 63),          # 퍼플 우드
            'grid': (139, 69, 19),            # 새들 브라운
            'black_stone': (0, 0, 0),         # 검은색
            'white_stone': (255, 255, 255),   # 흰색
            'text': (255, 255, 255),          # 흰색
            'highlight': (255, 215, 0),       # 골드
            'shadow': (105, 105, 105)         # 딤 그레이
        }
        
        # 보드 설정
        self.board_size = 10
        self.cell_size = min(screen_width, screen_height) // (self.board_size + 2)
        self.board_width = self.board_size * self.cell_size
        self.board_height = self.board_size * self.cell_size
        
        # 보드 위치 계산 (화면 중앙)
        self.board_x = (screen_width - self.board_width) // 2
        self.board_y = (screen_height - self.board_height) // 2
        self.board_rect = pygame.Rect(self.board_x, self.board_y, 
                                     self.board_width, self.board_height)
        
        # 폰트 초기화
        pygame.font.init()
        self.title_font = pygame.font.Font(None, 48)
        self.info_font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)
        
    def render_board(self, surface: pygame.Surface, board: Board):
        """
        오목판 렌더링
        
        Args:
            surface (pygame.Surface): 그릴 서피스
            board (Board): 게임 보드
        """
        # 보드 배경 (3D 효과)
        create_3d_effect(surface, self.board_rect, self.colors['board'], depth=5)
        
        # 격자 그리기
        for i in range(self.board_size + 1):
            # 세로선
            start_pos = (self.board_x + i * self.cell_size, self.board_y)
            end_pos = (self.board_x + i * self.cell_size, self.board_y + self.board_height)
            pygame.draw.line(surface, self.colors['grid'], start_pos, end_pos, 2)
            
            # 가로선
            start_pos = (self.board_x, self.board_y + i * self.cell_size)
            end_pos = (self.board_x + self.board_width, self.board_y + i * self.cell_size)
            pygame.draw.line(surface, self.colors['grid'], start_pos, end_pos, 2)
        
        # 돌 그리기
        board_state = board.get_board_state()
        for row in range(self.board_size):
            for col in range(self.board_size):
                if board_state[row, col] != 0:
                    self.render_stone(surface, row, col, board_state[row, col], board)
    
    def render_stone(self, surface: pygame.Surface, row: int, col: int, 
                    player: int, board: Board):
        """
        돌 렌더링 (3D 효과 포함)
        
        Args:
            surface (pygame.Surface): 그릴 서피스
            row (int): 행 인덱스
            col (int): 열 인덱스
            player (int): 플레이어 (1: 흑돌, 2: 백돌)
            board (Board): 게임 보드
        """
        # 돌 위치 계산
        x = self.board_x + col * self.cell_size + self.cell_size // 2
        y = self.board_y + row * self.cell_size + self.cell_size // 2
        radius = self.cell_size // 2 - 4
        
        # 돌 색상 선택
        color = self.colors['black_stone'] if player == 1 else self.colors['white_stone']
        
        # 3D 효과를 위한 그림자
        shadow_radius = radius + 2
        shadow_color = self.colors['shadow']
        pygame.draw.circle(surface, shadow_color, (x + 2, y + 2), shadow_radius)
        
        # 돌 그리기
        pygame.draw.circle(surface, color, (x, y), radius)
        
        # 하이라이트 효과 (흰돌의 경우)
        if player == 2:
            highlight_radius = radius // 3
            highlight_pos = (x - highlight_radius // 2, y - highlight_radius // 2)
            pygame.draw.circle(surface, (220, 220, 220), highlight_pos, highlight_radius)
        
        # 마지막 돌 하이라이트
        if board.last_move == (row, col):
            pygame.draw.circle(surface, self.colors['highlight'], (x, y), radius + 2, 3)
    
    def render_ui(self, surface: pygame.Surface, board: Board, game_mode: str):
        """
        UI 렌더링 (게임 정보, 상태 등)
        
        Args:
            surface (pygame.Surface): 그릴 서피스
            board (Board): 게임 보드
            game_mode (str): 게임 모드
        """
        # 게임 모드 표시
        mode_text = f"모드: {game_mode}"
        mode_surface = self.info_font.render(mode_text, True, self.colors['text'])
        surface.blit(mode_surface, (20, 20))
        
        # 현재 플레이어 표시
        current_player = board.get_current_player()
        player_text = "Black's Turn" if current_player == 1 else "White's Turn"
        player_color = self.colors['black_stone'] if current_player == 1 else self.colors['white_stone']
        draw_text_with_shadow(surface, player_text, self.info_font, player_color, (20, 60))
        
        # 게임 상태 확인
        game_over, winner = board.get_game_status()
        
        if game_over:
            if winner:
                winner_text = "Black Wins!" if winner == 1 else "White Wins!"
                winner_color = self.colors['black_stone'] if winner == 1 else self.colors['white_stone']
                draw_text_with_shadow(surface, winner_text, self.title_font, winner_color, 
                                   (self.screen_width // 2 - 100, 20))
            else:
                draw_text_with_shadow(surface, "Draw!", self.title_font, self.colors['text'], 
                                   (self.screen_width // 2 - 80, 20))
        
        # 조작법 안내
        controls = [
            "Controls:",
            "Mouse Click - Place stone",
            "R key - Restart game",
            "ESC key - Exit game",
            "1 key - 2-Player mode",
            "2 key - AI Battle mode",
            "S key - Toggle sound",
            "M key - Toggle music",
            "T key - Show statistics",
            "H key - Show history",
            "L key - Start replay",
            "Arrow keys - Navigate replay",
            "SPACE - Stop replay"
        ]
        
        y_offset = self.screen_height - 150
        for i, control in enumerate(controls):
            color = self.colors['highlight'] if i == 0 else self.colors['text']
            font = self.info_font if i == 0 else self.small_font
            draw_text_with_shadow(surface, control, font, color, (20, y_offset + i * 25))
    
    def render_loading_screen(self, surface: pygame.Surface, progress: float = 0.0):
        """
        로딩 화면 렌더링
        
        Args:
            surface (pygame.Surface): 그릴 서피스
            progress (float): 로딩 진행률 (0.0 ~ 1.0)
        """
        # 배경
        surface.fill(self.colors['background'])
        
        # 제목
        title_text = "3D Gomoku Game"
        draw_text_with_shadow(surface, title_text, self.title_font, self.colors['text'], 
                           (self.screen_width // 2 - 150, self.screen_height // 2 - 100))
        
        # 로딩 바
        bar_width = 400
        bar_height = 20
        bar_x = (self.screen_width - bar_width) // 2
        bar_y = self.screen_height // 2 + 50
        
        # 배경 바
        pygame.draw.rect(surface, self.colors['shadow'], 
                        (bar_x, bar_y, bar_width, bar_height))
        
        # 진행 바
        progress_width = int(bar_width * progress)
        pygame.draw.rect(surface, self.colors['highlight'], 
                        (bar_x, bar_y, progress_width, bar_height))
        
        # 진행률 텍스트
        progress_text = f"Loading... {int(progress * 100)}%"
        draw_text_with_shadow(surface, progress_text, self.info_font, self.colors['text'], 
                           (self.screen_width // 2 - 80, bar_y + 30))
    
    def get_board_rect(self) -> pygame.Rect:
        """
        보드 영역 반환
        
        Returns:
            pygame.Rect: 보드 영역
        """
        return self.board_rect
    
    def get_cell_size(self) -> int:
        """
        셀 크기 반환
        
        Returns:
            int: 셀 크기
        """
        return self.cell_size
    
    def render_replay_info(self, surface: pygame.Surface, replay_info: dict):
        """
        리플레이 정보 렌더링
        
        Args:
            surface (pygame.Surface): 그릴 서피스
            replay_info (dict): 리플레이 정보
        """
        if not replay_info:
            return
        
        # 리플레이 정보 텍스트
        info_text = f"Replay: Game {replay_info['game_id']} - Move {replay_info['current_move']}/{replay_info['total_moves']}"
        info_surface = self.info_font.render(info_text, True, self.colors['highlight'])
        surface.blit(info_surface, (self.screen_width // 2 - 150, 20))
        
        # 게임 모드 정보
        mode_text = f"Mode: {replay_info['game_mode']}"
        mode_surface = self.small_font.render(mode_text, True, self.colors['text'])
        surface.blit(mode_surface, (self.screen_width // 2 - 100, 50))
        
        # 승자 정보
        if replay_info['is_draw']:
            winner_text = "Result: Draw"
        else:
            winner_text = f"Winner: Player {replay_info['winner']}"
        winner_surface = self.small_font.render(winner_text, True, self.colors['text'])
        surface.blit(winner_surface, (self.screen_width // 2 - 100, 75))
        
        # 리플레이 컨트롤 안내
        controls_text = "Use LEFT/RIGHT arrows to navigate, SPACE to stop"
        controls_surface = self.small_font.render(controls_text, True, self.colors['highlight'])
        surface.blit(controls_surface, (self.screen_width // 2 - 200, self.screen_height - 50)) 