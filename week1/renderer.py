"""
3D 렌더링 클래스
게임의 3D 시각 효과와 렌더링을 담당합니다.
"""

import pygame
import math
from typing import Tuple, Optional
from board import Board
from utils import (create_3d_effect, create_stone_3d_effect, create_animated_3d_effect,
                   draw_text_with_shadow, draw_text_with_glow, board_to_screen_pos, 
                   create_gradient_surface, create_particle_effect)


class Renderer:
    """3D 오목 게임 렌더링 클래스"""
    
    def __init__(self, screen_width: int = 1400, screen_height: int = 900):
        """
        렌더러 초기화
        
        Args:
            screen_width (int): 화면 너비 (사이드바 400px + 바둑판 10x10)
            screen_height (int): 화면 높이
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # 애니메이션 시간 추적
        self.animation_time = 0.0
        
        # 색상 정의 (더 풍부한 색상 팔레트)
        self.colors = {
            'background': (25, 100, 25),      # 다크 포레스트 그린
            'board': (160, 82, 45),           # 새들 브라운
            'grid': (101, 67, 33),            # 다크 브라운
            'black_stone': (20, 20, 20),      # 다크 블랙
            'white_stone': (245, 245, 245),   # 오프 화이트
            'text': (255, 255, 255),          # 흰색
            'highlight': (255, 215, 0),       # 골드
            'shadow': (50, 50, 50),           # 다크 그레이
            'glow': (255, 255, 200),          # 글로우 색상
            'particle': (255, 255, 100)       # 파티클 색상
        }
        
        # 보드 설정 (사이드바를 제외한 공간에 맞춤)
        self.board_size = 10
        sidebar_width = 400
        available_width = screen_width - sidebar_width - 60  # 여백 30px씩
        available_height = screen_height - 60
        self.cell_size = min(available_width, available_height) // self.board_size
        self.board_width = self.board_size * self.cell_size
        self.board_height = self.board_size * self.cell_size
        
        # 보드 위치 계산 (사이드바를 제외한 영역의 중앙)
        self.board_x = (available_width - self.board_width) // 2 + 30  # 왼쪽 여백
        self.board_y = (screen_height - self.board_height) // 2
        self.board_rect = pygame.Rect(self.board_x, self.board_y, 
                                     self.board_width, self.board_height)
        
        # 폰트 초기화
        pygame.font.init()
        
        # 시스템 폰트 사용 (한글 지원)
        try:
            # Windows 시스템 폰트 시도
            self.title_font = pygame.font.Font("C:/Windows/Fonts/malgun.ttf", 48)
            self.info_font = pygame.font.Font("C:/Windows/Fonts/malgun.ttf", 32)
            self.small_font = pygame.font.Font("C:/Windows/Fonts/malgun.ttf", 24)
        except:
            try:
                # 기본 폰트 시도
                self.title_font = pygame.font.Font(None, 48)
                self.info_font = pygame.font.Font(None, 32)
                self.small_font = pygame.font.Font(None, 24)
            except:
                # 마지막 수단으로 기본 폰트
                self.title_font = pygame.font.SysFont(None, 48)
                self.info_font = pygame.font.SysFont(None, 32)
                self.small_font = pygame.font.SysFont(None, 24)
        
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
        돌 렌더링 (고급 3D 효과 포함)
        
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
        is_white = (player == 2)
        
        # 고급 3D 효과 적용
        create_stone_3d_effect(surface, (x, y), radius, color, is_white)
        
        # 마지막 돌 애니메이션 하이라이트
        if board.last_move == (row, col):
            # 펄스 애니메이션 효과
            pulse_factor = 1.0 + 0.1 * math.sin(self.animation_time * 8)
            pulse_radius = int(radius * pulse_factor)
            pygame.draw.circle(surface, self.colors['highlight'], (x, y), pulse_radius, 3)
            
            # 파티클 효과
            create_particle_effect(surface, (x, y), self.colors['particle'], 
                                 particle_count=8, time=self.animation_time % 1.0)
    
    def render_ui(self, surface: pygame.Surface, board: Board, game_mode: str, ai_difficulty: str = "Medium", ai_thinking: bool = False):
        """
        UI 렌더링 (게임 정보, 상태 등)
        
        Args:
            surface (pygame.Surface): 그릴 서피스
            board (Board): 게임 보드
            game_mode (str): 게임 모드
            ai_difficulty (str): AI 난이도
            ai_thinking (bool): AI가 계산 중인지 여부
        """
        # 오른쪽 사이드바 배경 (바둑판을 가리지 않음)
        sidebar_width = 400
        sidebar_rect = pygame.Rect(self.screen_width - sidebar_width, 0, sidebar_width, self.screen_height)
        
        # 사이드바 고급 그라데이션 배경
        gradient_surface = create_gradient_surface(sidebar_width, self.screen_height, 
                                                 (50, 50, 50), (25, 25, 25), "vertical")
        surface.blit(gradient_surface, sidebar_rect)
        
        # 사이드바 테두리
        pygame.draw.rect(surface, self.colors['highlight'], sidebar_rect, 2)
        
        # 게임 정보 (상단)
        info_x = self.screen_width - sidebar_width + 20
        info_y = 30
        
        # 게임 모드 표시 (글로우 효과)
        mode_text = f"Mode: {game_mode}"
        draw_text_with_glow(surface, mode_text, self.info_font, self.colors['highlight'], 
                           (info_x, info_y), glow_intensity=0.3)
        
        # AI 난이도 표시 (AI Battle 모드일 때만)
        if game_mode == "AI Battle":
            difficulty_text = f"AI: {ai_difficulty}"
            draw_text_with_shadow(surface, difficulty_text, self.small_font, self.colors['text'], (info_x, info_y + 25))
        
        # 현재 플레이어 표시
        current_player = board.get_current_player()
        if ai_thinking and game_mode == "AI Battle" and current_player == 2:
            player_text = "AI is thinking..."
            player_color = self.colors['highlight']
        else:
            player_text = "Black's Turn" if current_player == 1 else "White's Turn"
            player_color = self.colors['black_stone'] if current_player == 1 else self.colors['white_stone']
        draw_text_with_shadow(surface, player_text, self.info_font, player_color, (info_x, info_y + 40))
        
        # 게임 상태 확인
        game_over, winner = board.get_game_status()
        
        if game_over:
            if winner:
                winner_text = "Black Wins!" if winner == 1 else "White Wins!"
                winner_color = self.colors['black_stone'] if winner == 1 else self.colors['white_stone']
                draw_text_with_shadow(surface, winner_text, self.title_font, winner_color, (info_x, info_y + 80))
            else:
                draw_text_with_shadow(surface, "Draw!", self.title_font, self.colors['text'], (info_x, info_y + 80))
        
        # Controls 섹션 (중간)
        controls_y = info_y + 200
        draw_text_with_shadow(surface, "Controls:", self.info_font, self.colors['highlight'], (info_x, controls_y))
        
        # 디버그 모드 컨트롤 추가
        debug_controls = [
            "F1: Debug Mode",
            "F2: Auto Test",
            "F3: Validate State"
        ]
        
        for i, control in enumerate(debug_controls):
            draw_text_with_shadow(surface, control, self.small_font, self.colors['text'], 
                                (info_x, controls_y + 40 + i * 25))
        controls_y = 200
        draw_text_with_shadow(surface, "GAME CONTROLS", self.info_font, self.colors['highlight'], (info_x, controls_y))
        
        game_controls = [
            "Mouse Click - Place stone",
            "R - Restart game",
            "ESC - Exit/Close popup",
            "1 - 2-Player mode",
            "2 - AI battle mode",
            "3 - Change AI difficulty"
        ]
        
        for i, control in enumerate(game_controls):
            draw_text_with_shadow(surface, control, self.small_font, self.colors['text'], 
                               (info_x, controls_y + 40 + i * 20))
        
        # 사운드 컨트롤
        sound_y = controls_y + 160
        draw_text_with_shadow(surface, "SOUND CONTROLS", self.info_font, self.colors['highlight'], (info_x, sound_y))
        
        sound_controls = [
            "S - Toggle sound",
            "M - Toggle music"
        ]
        
        for i, control in enumerate(sound_controls):
            draw_text_with_shadow(surface, control, self.small_font, self.colors['text'], 
                               (info_x, sound_y + 40 + i * 20))
        
        # 리플레이 컨트롤
        replay_y = sound_y + 120
        draw_text_with_shadow(surface, "REPLAY CONTROLS", self.info_font, self.colors['highlight'], (info_x, replay_y))
        
        replay_controls = [
            "T - Show statistics",
            "H - Show history",
            "L - Start replay",
            "UP/DOWN - Select replay",
            "ENTER - Play replay",
            "LEFT/RIGHT - Move step",
            "SPACE - Stop replay"
        ]
        
        for i, control in enumerate(replay_controls):
            draw_text_with_shadow(surface, control, self.small_font, self.colors['text'], 
                               (info_x, replay_y + 40 + i * 20))
        
        # AI 계산 중 로딩 애니메이션 (바둑판 위에 표시)
        if ai_thinking and game_mode == "AI Battle":
            self.render_ai_thinking_animation(surface)
    
    def render_ai_thinking_animation(self, surface: pygame.Surface):
        """
        AI 계산 중 로딩 애니메이션 렌더링 (바둑판 위에 표시)
        
        Args:
            surface (pygame.Surface): 그릴 서피스
        """
        # 반투명 오버레이 (바둑판 위에)
        overlay = pygame.Surface((self.board_width, self.board_height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (self.board_x, self.board_y))
        
        # 로딩 모달 배경
        modal_width = 400
        modal_height = 200
        modal_x = self.board_x + (self.board_width - modal_width) // 2
        modal_y = self.board_y + (self.board_height - modal_height) // 2
        modal_rect = pygame.Rect(modal_x, modal_y, modal_width, modal_height)
        
        # 모달 배경 그라데이션
        gradient_surface = create_gradient_surface(modal_width, modal_height, (50, 50, 60), (30, 30, 40))
        surface.blit(gradient_surface, modal_rect)
        
        # 모달 테두리
        pygame.draw.rect(surface, self.colors['highlight'], modal_rect, 3, border_radius=15)
        
        # AI 아이콘 (원형)
        icon_center_x = modal_x + modal_width // 2
        icon_center_y = modal_y + 50
        icon_radius = 25
        
        # 아이콘 배경
        pygame.draw.circle(surface, (40, 40, 50), (icon_center_x, icon_center_y), icon_radius + 2)
        pygame.draw.circle(surface, self.colors['highlight'], (icon_center_x, icon_center_y), icon_radius, 2)
        
        # AI 텍스트
        ai_text = "AI"
        ai_surface = self.info_font.render(ai_text, True, self.colors['highlight'])
        ai_rect = ai_surface.get_rect(center=(icon_center_x, icon_center_y))
        surface.blit(ai_surface, ai_rect)
        
        # 로딩 텍스트
        loading_text = "Thinking..."
        loading_surface = self.info_font.render(loading_text, True, self.colors['text'])
        loading_rect = loading_surface.get_rect(center=(modal_x + modal_width // 2, modal_y + 100))
        surface.blit(loading_surface, loading_rect)
        
        # 로딩 바
        bar_width = 300
        bar_height = 8
        bar_x = modal_x + (modal_width - bar_width) // 2
        bar_y = modal_y + 130
        
        # 로딩 바 배경
        bar_bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(surface, (40, 40, 40), bar_bg_rect, border_radius=4)
        pygame.draw.rect(surface, (60, 60, 60), bar_bg_rect, 1, border_radius=4)
        
        # 애니메이션 진행 바
        import time
        progress = (time.time() * 1.2) % 1.0  # 0.83초 주기로 애니메이션
        progress_width = int(bar_width * progress)
        progress_rect = pygame.Rect(bar_x, bar_y, progress_width, bar_height)
        pygame.draw.rect(surface, self.colors['highlight'], progress_rect, border_radius=4)
        
        # 점 애니메이션
        dots = int((time.time() * 2) % 4)
        dots_text = "." * dots
        dots_surface = self.small_font.render(dots_text, True, self.colors['highlight'])
        dots_rect = dots_surface.get_rect(center=(modal_x + modal_width // 2, modal_y + 160))
        surface.blit(dots_surface, dots_rect)
    
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
    
    def update_animation_time(self, delta_time: float):
        """
        애니메이션 시간 업데이트
        
        Args:
            delta_time (float): 경과 시간 (초)
        """
        self.animation_time += delta_time
    
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

    def get_popup_rect(self) -> pygame.Rect:
        width = 700  # 500에서 700으로 증가
        height = 600  # 400에서 600으로 증가
        x = (self.screen_width - width) // 2
        y = (self.screen_height - height) // 2
        return pygame.Rect(x, y, width, height)

    def render_stats_popup(self, surface, stats):
        rect = self.get_popup_rect()
        pygame.draw.rect(surface, (30, 30, 30), rect, border_radius=16)
        pygame.draw.rect(surface, self.colors['highlight'], rect, 3, border_radius=16)
        draw_text_with_shadow(surface, "Game Statistics", self.title_font, self.colors['highlight'], (rect.x + 30, rect.y + 20))
        lines = [
            f"Total Games: {stats['total_games']}",
            f"Win Rate - Black: {stats['win_rate']['black']:.1f}%, White: {stats['win_rate']['white']:.1f}%, Draw: {stats['win_rate']['draw']:.1f}%",
            f"Average Duration: {stats['average_duration']:.1f} sec",
            f"Average Moves: {stats['average_moves']:.1f}",
            f"Longest Game: {stats['longest_game']:.1f} sec",
            f"Shortest Game: {stats['shortest_game']:.1f} sec",
            f"AI Wins: {stats['ai_performance']['wins']}, Losses: {stats['ai_performance']['losses']}, Win Rate: {stats['ai_performance']['win_rate']:.1f}%"
        ]
        for i, line in enumerate(lines):
            draw_text_with_shadow(surface, line, self.info_font, self.colors['text'], (rect.x + 30, rect.y + 80 + i * 45))  # 간격 35에서 45로 증가
        draw_text_with_shadow(surface, "ESC to close", self.small_font, self.colors['highlight'], (rect.x + 30, rect.y + rect.height - 40))

    def render_history_popup(self, surface, games):
        rect = self.get_popup_rect()
        pygame.draw.rect(surface, (30, 30, 30), rect, border_radius=16)
        pygame.draw.rect(surface, self.colors['highlight'], rect, 3, border_radius=16)
        draw_text_with_shadow(surface, "Recent Games", self.title_font, self.colors['highlight'], (rect.x + 30, rect.y + 20))
        if not games:
            draw_text_with_shadow(surface, "No games played yet.", self.info_font, self.colors['text'], (rect.x + 30, rect.y + 80))
        else:
            for i, game in enumerate(games):
                winner_text = "Draw" if game['is_draw'] else f"Player {game['winner']}"
                line = f"{game['id']}: {game['game_mode']} - {winner_text} ({game['total_moves']} moves)"
                draw_text_with_shadow(surface, line, self.small_font, self.colors['text'], (rect.x + 30, rect.y + 80 + i * 35))  # 간격 30에서 35로 증가
        draw_text_with_shadow(surface, "ESC to close", self.small_font, self.colors['highlight'], (rect.x + 30, rect.y + rect.height - 40))

    def render_replay_select_popup(self, surface, games, selected_idx):
        rect = self.get_popup_rect()
        pygame.draw.rect(surface, (30, 30, 30), rect, border_radius=16)
        pygame.draw.rect(surface, self.colors['highlight'], rect, 3, border_radius=16)
        draw_text_with_shadow(surface, "Select Game to Replay", self.title_font, self.colors['highlight'], (rect.x + 30, rect.y + 20))
        if not games:
            draw_text_with_shadow(surface, "No games available.", self.info_font, self.colors['text'], (rect.x + 30, rect.y + 80))
        else:
            for i, game in enumerate(games):
                winner_text = "Draw" if game['is_draw'] else f"Player {game['winner']}"
                line = f"{game['id']}: {game['game_mode']} - {winner_text}"
                color = self.colors['highlight'] if i == selected_idx else self.colors['text']
                draw_text_with_shadow(surface, line, self.info_font, color, (rect.x + 30, rect.y + 60 + i * 45))  # 간격 40에서 45로 증가
        draw_text_with_shadow(surface, "UP/DOWN: select, ENTER: replay, ESC: close", self.small_font, self.colors['highlight'], (rect.x + 30, rect.y + rect.height - 40))

    def render_message_popup(self, surface, message):
        rect = self.get_popup_rect()
        pygame.draw.rect(surface, (30, 30, 30), rect, border_radius=16)
        pygame.draw.rect(surface, self.colors['highlight'], rect, 3, border_radius=16)
        draw_text_with_shadow(surface, message, self.info_font, self.colors['highlight'], (rect.x + 30, rect.y + rect.height // 2 - 20))
        draw_text_with_shadow(surface, "ESC to close", self.small_font, self.colors['highlight'], (rect.x + 30, rect.y + rect.height - 40))

    def render_winner_popup(self, surface, winner, game_mode):
        """
        게임 종료 시 승리 모달 렌더링
        
        Args:
            surface (pygame.Surface): 그릴 서피스
            winner (int): 승자 (1: 흑돌, 2: 백돌, None: 무승부)
            game_mode (str): 게임 모드
        """
        rect = self.get_popup_rect()
        
        # 반투명 오버레이 (배경 어둡게)
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))
        
        # 모달 배경 (더 큰 크기로 변경)
        modal_width = 800
        modal_height = 650
        modal_x = (self.screen_width - modal_width) // 2
        modal_y = (self.screen_height - modal_height) // 2
        modal_rect = pygame.Rect(modal_x, modal_y, modal_width, modal_height)
        
        # 모달 배경 그라데이션 (더 세련된 색상)
        gradient_surface = create_gradient_surface(modal_width, modal_height, (45, 45, 55), (25, 25, 35))
        surface.blit(gradient_surface, modal_rect)
        
        # 모달 테두리 (더 두껍고 세련된)
        pygame.draw.rect(surface, self.colors['highlight'], modal_rect, 4, border_radius=20)
        
        # 내부 테두리 (더 세련된 효과)
        inner_rect = pygame.Rect(modal_x + 2, modal_y + 2, modal_width - 4, modal_height - 4)
        pygame.draw.rect(surface, (60, 60, 70), inner_rect, 2, border_radius=18)
        
        # 제목 섹션
        title_y = modal_y + 50
        title_text = "GAME OVER"
        title_surface = self.title_font.render(title_text, True, self.colors['highlight'])
        title_rect = title_surface.get_rect(center=(modal_x + modal_width // 2, title_y))
        surface.blit(title_surface, title_rect)
        
        # 승자 표시 섹션 (중앙 정렬)
        winner_y = modal_y + 150
        if winner:
            winner_text = "BLACK WINS!" if winner == 1 else "WHITE WINS!"
            winner_color = self.colors['black_stone'] if winner == 1 else self.colors['white_stone']
            
            # 승자 텍스트
            winner_surface = self.title_font.render(winner_text, True, winner_color)
            winner_rect = winner_surface.get_rect(center=(modal_x + modal_width // 2, winner_y))
            surface.blit(winner_surface, winner_rect)
            
            # 승리 돌 표시 (더 크고 세련된)
            stone_x = modal_x + modal_width // 2
            stone_y = winner_y + 80
            stone_radius = 40
            stone_color = self.colors['black_stone'] if winner == 1 else self.colors['white_stone']
            
            # 돌 그림자 (더 부드러운)
            shadow_radius = stone_radius + 4
            pygame.draw.circle(surface, (20, 20, 20), (stone_x + 4, stone_y + 4), shadow_radius)
            
            # 돌 그라데이션 효과
            for i in range(stone_radius, 0, -2):
                alpha = 255 - (stone_radius - i) * 10
                if alpha > 0:
                    temp_surface = pygame.Surface((stone_radius * 2, stone_radius * 2), pygame.SRCALPHA)
                    pygame.draw.circle(temp_surface, (*stone_color, alpha), (stone_radius, stone_radius), i)
                    surface.blit(temp_surface, (stone_x - stone_radius, stone_y - stone_radius))
            
            # 메인 돌
            pygame.draw.circle(surface, stone_color, (stone_x, stone_y), stone_radius)
            
            # 하이라이트 (흰돌의 경우)
            if winner == 2:
                highlight_radius = stone_radius // 3
                highlight_pos = (stone_x - highlight_radius // 2, stone_y - highlight_radius // 2)
                pygame.draw.circle(surface, (240, 240, 240), highlight_pos, highlight_radius)
            
            # 승리 돌 테두리
            pygame.draw.circle(surface, self.colors['highlight'], (stone_x, stone_y), stone_radius + 2, 3)
            
        else:
            # 무승부 표시
            draw_text = "DRAW!"
            draw_surface = self.title_font.render(draw_text, True, self.colors['text'])
            draw_rect = draw_surface.get_rect(center=(modal_x + modal_width // 2, winner_y))
            surface.blit(draw_surface, draw_rect)
        
        # 게임 정보 섹션 (중앙 정렬)
        info_y = modal_y + 350
        info_bg_rect = pygame.Rect(modal_x + 50, info_y - 20, modal_width - 100, 80)
        pygame.draw.rect(surface, (35, 35, 45), info_bg_rect, border_radius=15)
        pygame.draw.rect(surface, (70, 70, 80), info_bg_rect, 2, border_radius=15)
        
        # 게임 모드
        mode_text = f"Game Mode: {game_mode}"
        mode_surface = self.info_font.render(mode_text, True, self.colors['text'])
        mode_rect = mode_surface.get_rect(center=(modal_x + modal_width // 2, info_y))
        surface.blit(mode_surface, mode_rect)
        
        # 게임 종료 시간 (현재 시간 표시)
        import datetime
        time_text = f"Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
        time_surface = self.small_font.render(time_text, True, (150, 150, 150))
        time_rect = time_surface.get_rect(center=(modal_x + modal_width // 2, info_y + 35))
        surface.blit(time_surface, time_rect)
        
        # 컨트롤 안내 섹션 (하단)
        control_y = modal_y + 500
        control_bg_rect = pygame.Rect(modal_x + 50, control_y - 15, modal_width - 100, 60)
        pygame.draw.rect(surface, (40, 40, 50), control_bg_rect, border_radius=12)
        pygame.draw.rect(surface, self.colors['highlight'], control_bg_rect, 2, border_radius=12)
        
        # 컨트롤 텍스트들
        controls = [
            ("Press R", "Restart Game"),
            ("Press ESC", "Continue"),
            ("Press H", "View History")
        ]
        
        for i, (key, desc) in enumerate(controls):
            control_x = modal_x + 100 + i * 200
            key_surface = self.small_font.render(key, True, self.colors['highlight'])
            desc_surface = self.small_font.render(desc, True, (150, 150, 150))
            
            key_rect = key_surface.get_rect(center=(control_x, control_y))
            desc_rect = desc_surface.get_rect(center=(control_x, control_y + 25))
            
            surface.blit(key_surface, key_rect)
            surface.blit(desc_surface, desc_rect)
        
        # 장식 요소들
        # 상단 장식선
        decor_y = modal_y + 30
        pygame.draw.line(surface, self.colors['highlight'], 
                        (modal_x + 100, decor_y), (modal_x + modal_width - 100, decor_y), 3)
        
        # 하단 장식선
        decor_y2 = modal_y + modal_height - 30
        pygame.draw.line(surface, self.colors['highlight'], 
                        (modal_x + 100, decor_y2), (modal_x + modal_width - 100, decor_y2), 3) 