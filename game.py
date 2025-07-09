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
from sound_manager import SoundManager
from game_stats import GameStats
from game_history import GameHistory


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
        self.sound_manager = SoundManager()
        self.game_stats = GameStats()
        self.game_history = GameHistory()
        
        # 게임 상태
        self.game_mode = "2-Player"  # "2-Player" 또는 "AI Battle"
        self.running = True
        self.clock = pygame.time.Clock()
        
        # 게임 시작
        self.sound_manager.play_start()
        self.game_stats.start_new_game(self.game_mode)
        
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
        elif key == pygame.K_s:
            self.sound_manager.toggle_sound()
        elif key == pygame.K_m:
            self.sound_manager.toggle_music()
        elif key == pygame.K_t:
            self.show_statistics()
        elif key == pygame.K_h:
            self.show_history()
        elif key == pygame.K_l:
            self.start_replay_mode()
        elif key == pygame.K_RIGHT:
            self.next_replay_move()
        elif key == pygame.K_LEFT:
            self.previous_replay_move()
        elif key == pygame.K_SPACE:
            self.stop_replay()
    
    def handle_mouse_click(self, pos):
        """마우스 클릭 처리"""
        # 보드 영역 확인
        board_rect = self.renderer.get_board_rect()
        cell_size = self.renderer.get_cell_size()
        
        board_pos = screen_to_board_pos(pos, board_rect, cell_size)
        
        if board_pos:
            row, col = board_pos
            if self.board.place_stone(row, col):
                # 사운드 재생 및 통계 기록
                self.sound_manager.play_stone_place()
                self.game_stats.record_move(self.board.get_current_player(), row, col)
                
                # AI 대전 모드에서 AI 차례 처리
                if self.game_mode == "AI Battle" and not self.board.game_over:
                    self.handle_ai_turn()
            else:
                # 유효하지 않은 수
                self.sound_manager.play_invalid()
    
    def handle_ai_turn(self):
        """AI 차례 처리"""
        if self.board.get_current_player() == self.ai.player:
            # AI 수 계산
            ai_move = self.ai.get_move(self.board)
            
            if ai_move:
                row, col = ai_move
                if self.board.place_stone(row, col):
                    # 사운드 재생 및 통계 기록
                    self.sound_manager.play_stone_place()
                    self.game_stats.record_move(self.board.get_current_player(), row, col)
    
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
        self.game_stats.start_new_game(self.game_mode)
        self.sound_manager.play_click()
    
    def show_statistics(self):
        """게임 통계 표시"""
        stats = self.game_stats.get_stats_summary()
        print("\n" + "="*50)
        print("GAME STATISTICS")
        print("="*50)
        print(f"Total Games: {stats['total_games']}")
        print(f"Win Rate - Black: {stats['win_rate']['black']:.1f}%, White: {stats['win_rate']['white']:.1f}%, Draw: {stats['win_rate']['draw']:.1f}%")
        print(f"Average Duration: {stats['average_duration']:.1f} seconds")
        print(f"Average Moves: {stats['average_moves']:.1f}")
        print(f"Longest Game: {stats['longest_game']:.1f} seconds")
        print(f"Shortest Game: {stats['shortest_game']:.1f} seconds")
        print(f"AI Performance - Wins: {stats['ai_performance']['wins']}, Losses: {stats['ai_performance']['losses']}, Win Rate: {stats['ai_performance']['win_rate']:.1f}%")
        print("="*50)
    
    def show_history(self):
        """게임 히스토리 표시"""
        recent_games = self.game_history.get_recent_games(10)
        print("\n" + "="*50)
        print("RECENT GAMES")
        print("="*50)
        if not recent_games:
            print("No games played yet.")
        else:
            for game in recent_games:
                winner_text = "Draw" if game['is_draw'] else f"Player {game['winner']}"
                print(f"Game {game['id']}: {game['game_mode']} - {winner_text} ({game['total_moves']} moves)")
        print("="*50)
    
    def start_replay_mode(self):
        """리플레이 모드 시작"""
        recent_games = self.game_history.get_recent_games(5)
        if not recent_games:
            print("No games available for replay.")
            return
        
        print("\n" + "="*50)
        print("SELECT GAME TO REPLAY")
        print("="*50)
        for game in recent_games:
            winner_text = "Draw" if game['is_draw'] else f"Player {game['winner']}"
            print(f"{game['id']}: {game['game_mode']} - {winner_text}")
        
        try:
            game_id = int(input("Enter game ID to replay: "))
            if self.game_history.start_replay(game_id):
                print(f"Started replay of game {game_id}")
                print("Use LEFT/RIGHT arrows to navigate, SPACE to stop")
            else:
                print("Invalid game ID")
        except ValueError:
            print("Invalid input")
    
    def next_replay_move(self):
        """리플레이에서 다음 수로 이동"""
        if self.game_history.is_replaying:
            if self.game_history.next_move():
                self.sound_manager.play_click()
            else:
                print("End of replay")
    
    def previous_replay_move(self):
        """리플레이에서 이전 수로 이동"""
        if self.game_history.is_replaying:
            if self.game_history.previous_move():
                self.sound_manager.play_click()
            else:
                print("Beginning of replay")
    
    def stop_replay(self):
        """리플레이 중지"""
        if self.game_history.is_replaying:
            self.game_history.stop_replay()
            print("Replay stopped")
    
    def update(self):
        """게임 상태 업데이트"""
        # 게임 종료 조건 확인
        game_over, winner = self.board.get_game_status()
        
        if game_over:
            # 게임 종료 처리
            self.game_stats.end_game(winner, game_over)
            
            # 히스토리에 게임 추가
            game_data = {
                'game_mode': self.game_mode,
                'winner': winner,
                'is_draw': not winner,
                'duration': self.game_stats.current_game['duration'],
                'total_moves': len(self.game_stats.current_game['moves']),
                'moves': self.game_stats.current_game['moves'],
                'board_size': self.board.size,
                'ai_performance': self.game_stats.stats['ai_performance']
            }
            self.game_history.add_game(game_data)
            
            if winner:
                self.sound_manager.play_win()
            
            # 게임 종료 시 잠시 대기
            pygame.time.wait(2000)
            self.restart_game()
    
    def render(self):
        """게임 렌더링"""
        # 배경 그리기
        self.screen.fill(self.renderer.colors['background'])
        
        # 리플레이 모드인지 확인
        if self.game_history.is_replaying:
            replay_board = self.game_history.get_replay_board()
            if replay_board:
                # 리플레이 보드 렌더링
                self.renderer.render_board(self.screen, replay_board)
                # 리플레이 정보 표시
                self.renderer.render_replay_info(self.screen, self.game_history.get_replay_info())
            else:
                # 일반 보드 렌더링
                self.renderer.render_board(self.screen, self.board)
        else:
            # 일반 보드 렌더링
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