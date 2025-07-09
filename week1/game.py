"""
게임 클래스
오목 게임의 메인 로직과 상태 관리를 담당합니다.
"""

import pygame
import time
import traceback
from typing import Optional, Tuple
from board import Board
from renderer import Renderer
from ai import AI
from utils import screen_to_board_pos, debug_log
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
        
        # 디버그 모드 설정
        self.debug_mode = False
        self.auto_test_mode = False
        self.test_moves = []
        
        # 게임 설정
        self.settings = {
            'sound_enabled': True,
            'music_enabled': True,
            'auto_save': True,
            'show_fps': False,
            'ai_thinking_time': 1.0,
            'board_size': 10
        }
        
        # Pygame 초기화
        try:
            pygame.init()
            self.screen = pygame.display.set_mode((screen_width, screen_height))
            pygame.display.set_caption("3D Gomoku Game - Debug Mode" if self.debug_mode else "3D Gomoku Game")
            debug_log("Pygame 초기화 성공", "INFO")
        except Exception as e:
            debug_log(f"Pygame 초기화 실패: {e}", "ERROR")
            raise
        
        # 게임 컴포넌트 초기화
        try:
            self.board = Board()
            self.renderer = Renderer(screen_width, screen_height)
            self.ai = AI(player=2, difficulty="Medium")  # AI는 백돌, 기본 난이도 Medium
            self.sound_manager = SoundManager()
            self.game_stats = GameStats()
            self.game_history = GameHistory()
            debug_log("게임 컴포넌트 초기화 성공", "INFO")
        except Exception as e:
            debug_log(f"게임 컴포넌트 초기화 실패: {e}", "ERROR")
            raise
        
        # 게임 상태
        self.game_mode = "2-Player"  # "2-Player" 또는 "AI Battle"
        self.ai_difficulty = "Medium"  # AI 난이도
        self.running = True
        self.clock = pygame.time.Clock()
        
        # AI 계산 상태
        self.ai_thinking = False
        self.ai_thinking_start_time = 0
        
        # 게임 시작
        try:
            self.sound_manager.play_start()
            self.game_stats.start_new_game(self.game_mode)
            debug_log("게임 시작 성공", "INFO")
        except Exception as e:
            debug_log(f"게임 시작 실패: {e}", "WARNING")
        
        # 로딩 화면 표시
        self.show_loading_screen()
        
        self.ui_mode = 'normal'  # 'normal', 'stats', 'history', 'replay_select', 'replay', 'message', 'winner', 'settings'
        self.popup_message = ''
        self.replay_select_index = 0
        self.replay_select_list = []
        self.winner_info = None  # 승리 정보 저장
        
        # 성능 모니터링
        self.frame_count = 0
        self.fps_start_time = time.time()
        self.last_fps = 60.0
        
        # 설정 로드
        self.load_settings()
    
    def show_loading_screen(self):
        """로딩 화면 표시"""
        try:
            for i in range(101):
                self.renderer.render_loading_screen(self.screen, i / 100)
                pygame.display.flip()
                pygame.time.wait(20)
            debug_log("로딩 화면 표시 완료", "INFO")
        except Exception as e:
            debug_log(f"로딩 화면 표시 실패: {e}", "WARNING")
    
    def handle_events(self):
        """이벤트 처리"""
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                elif event.type == pygame.KEYDOWN:
                    self.handle_keydown(event.key)
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # 왼쪽 클릭
                        self.handle_mouse_click(event.pos)
        except Exception as e:
            debug_log(f"이벤트 처리 오류: {e}", "ERROR")
            traceback.print_exc()
    
    def handle_keydown(self, key):
        """키보드 이벤트 처리"""
        try:
            if self.ui_mode == 'normal':
                if key == pygame.K_ESCAPE:
                    self.running = False
                elif key == pygame.K_r:
                    self.restart_game()
                elif key == pygame.K_1:
                    self.set_game_mode("2-Player")
                elif key == pygame.K_2:
                    self.set_game_mode("AI Battle")
                elif key == pygame.K_3:
                    self.cycle_ai_difficulty()
                elif key == pygame.K_s:
                    self.sound_manager.toggle_sound()
                elif key == pygame.K_m:
                    self.sound_manager.toggle_music()
                elif key == pygame.K_t:
                    self.ui_mode = 'stats'
                elif key == pygame.K_h:
                    self.ui_mode = 'history'
                elif key == pygame.K_l:
                    self.ui_mode = 'replay_select'
                    self.replay_select_list = self.game_history.get_recent_games(5)
                    self.replay_select_index = 0
                elif key == pygame.K_F1:  # 디버그 모드 토글
                    self.toggle_debug_mode()
                elif key == pygame.K_F2:  # 자동 테스트 모드
                    self.toggle_auto_test_mode()
                elif key == pygame.K_F3:  # 게임 상태 검증
                    self.validate_game_state()
                elif key == pygame.K_F4:  # 설정 메뉴
                    self.ui_mode = 'settings'
                elif key == pygame.K_F5:  # 통계 내보내기
                    self.export_statistics()
                elif key == pygame.K_F6:  # 게임 저장
                    self.save_game()
                elif key == pygame.K_F7:  # 게임 불러오기
                    self.load_game()
            elif self.ui_mode == 'stats' or self.ui_mode == 'history' or self.ui_mode == 'message':
                if key == pygame.K_ESCAPE:
                    self.ui_mode = 'normal'
            elif self.ui_mode == 'winner':
                if key == pygame.K_ESCAPE or key == pygame.K_r:
                    self.ui_mode = 'normal'
                    self.restart_game()
            elif self.ui_mode == 'replay_select':
                if key == pygame.K_ESCAPE:
                    self.ui_mode = 'normal'
                elif key == pygame.K_UP:
                    self.replay_select_index = max(0, self.replay_select_index - 1)
                elif key == pygame.K_DOWN:
                    self.replay_select_index = min(len(self.replay_select_list) - 1, self.replay_select_index + 1)
                elif key == pygame.K_RETURN or key == pygame.K_KP_ENTER:
                    if self.replay_select_list:
                        game_id = self.replay_select_list[self.replay_select_index]['id']
                        if self.game_history.start_replay(game_id):
                            self.ui_mode = 'replay'
                        else:
                            self.popup_message = 'Replay failed.'
                            self.ui_mode = 'message'
            elif self.ui_mode == 'replay':
                if key == pygame.K_ESCAPE or key == pygame.K_SPACE:
                    self.game_history.stop_replay()
                    self.ui_mode = 'normal'
                elif key == pygame.K_RIGHT:
                    self.game_history.next_move()
                elif key == pygame.K_LEFT:
                    self.game_history.previous_move()
        except Exception as e:
            debug_log(f"키보드 이벤트 처리 오류: {e}", "ERROR")
    
    def handle_mouse_click(self, pos):
        """마우스 클릭 처리"""
        try:
            if self.ui_mode == 'normal':
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
                        
                        # 디버그 모드에서 수 기록
                        if self.debug_mode:
                            debug_log(f"돌 배치: ({row}, {col}) - 플레이어 {self.board.get_current_player()}", "DEBUG")
                        
                        # AI 대전 모드에서 AI 차례 처리 (즉시 시작하지 않고 지연)
                        if self.game_mode == "AI Battle" and not self.board.game_over:
                            # AI 차례 시작 (지연된 실행)
                            self.handle_ai_turn()
                    else:
                        # 유효하지 않은 수
                        self.sound_manager.play_invalid()
                        if self.debug_mode:
                            debug_log(f"유효하지 않은 수: ({row}, {col})", "WARNING")
            elif self.ui_mode == 'replay_select':
                # 마우스 클릭으로 리플레이 선택
                mx, my = pos
                popup_rect = self.renderer.get_popup_rect()
                if popup_rect.collidepoint(mx, my):
                    idx = (my - popup_rect.y - 60) // 40
                    if 0 <= idx < len(self.replay_select_list):
                        self.replay_select_index = idx
                        game_id = self.replay_select_list[self.replay_select_index]['id']
                        if self.game_history.start_replay(game_id):
                            self.ui_mode = 'replay'
                        else:
                            self.popup_message = 'Replay failed.'
                            self.ui_mode = 'message'
        except Exception as e:
            debug_log(f"마우스 클릭 처리 오류: {e}", "ERROR")
    
    def handle_ai_turn(self):
        """AI 차례 처리"""
        if self.board.get_current_player() == self.ai.player and not self.ai_thinking:
            # AI 계산 시작
            self.ai_thinking = True
            self.ai_thinking_start_time = pygame.time.get_ticks()
            if self.debug_mode:
                debug_log("AI 계산 시작", "DEBUG")
    
    def update_ai_turn(self):
        """AI 차례 업데이트 (매 프레임 호출)"""
        if self.ai_thinking:
            current_time = pygame.time.get_ticks()
            thinking_duration = current_time - self.ai_thinking_start_time
            
            # AI 난이도에 따른 계산 시간 조정 (성능 향상으로 단축)
            difficulty_times = {
                "Easy": 200,
                "Medium": 400,
                "Hard": 800,
                "Expert": 1200
            }
            target_time = difficulty_times.get(self.ai_difficulty, 400)
            
            if thinking_duration >= target_time:
                try:
                    # AI 수 계산 및 실행
                    ai_move = self.ai.get_move(self.board)
                    if ai_move:
                        row, col = ai_move
                        if self.board.place_stone(row, col):
                            # 사운드 재생 및 통계 기록
                            self.sound_manager.play_stone_place()
                            self.game_stats.record_move(self.board.get_current_player(), row, col)
                            
                            if self.debug_mode:
                                debug_log(f"AI 수: ({row}, {col}) - 난이도 {self.ai_difficulty}", "DEBUG")
                        else:
                            debug_log(f"AI가 유효하지 않은 수를 선택: ({row}, {col})", "WARNING")
                    else:
                        debug_log("AI가 수를 선택하지 못함", "WARNING")
                except Exception as e:
                    debug_log(f"AI 계산 오류: {e}", "ERROR")
                
                self.ai_thinking = False
    
    def toggle_debug_mode(self):
        """디버그 모드 토글"""
        self.debug_mode = not self.debug_mode
        debug_log(f"디버그 모드: {'ON' if self.debug_mode else 'OFF'}", "INFO")
        pygame.display.set_caption("3D Gomoku Game - Debug Mode" if self.debug_mode else "3D Gomoku Game")
    
    def toggle_auto_test_mode(self):
        """자동 테스트 모드 토글"""
        self.auto_test_mode = not self.auto_test_mode
        if self.auto_test_mode:
            debug_log("자동 테스트 모드 시작", "INFO")
            self.start_auto_test()
        else:
            debug_log("자동 테스트 모드 종료", "INFO")
    
    def start_auto_test(self):
        """자동 테스트 시작"""
        # 간단한 테스트 시나리오
        self.test_moves = [
            (4, 4), (4, 5), (5, 4), (5, 5),  # 중앙 영역
            (3, 4), (4, 3), (6, 4), (4, 6),  # 중앙 주변
            (2, 4), (4, 2), (7, 4), (4, 7)   # 바깥쪽
        ]
        debug_log(f"자동 테스트 시나리오 로드: {len(self.test_moves)} 수", "INFO")
    
    def validate_game_state(self):
        """게임 상태 검증"""
        try:
            # 보드 상태 검증
            board_state = self.board.get_board_state()
            stone_count = (board_state != 0).sum()
            
            # 게임 상태 검증
            game_over, winner = self.board.get_game_status()
            current_player = self.board.get_current_player()
            
            # 통계 검증
            stats = self.game_stats.get_stats_summary()
            
            validation_result = {
                'board_valid': True,
                'stone_count': stone_count,
                'game_over': game_over,
                'winner': winner,
                'current_player': current_player,
                'total_games': stats['total_games'],
                'ai_thinking': self.ai_thinking,
                'game_mode': self.game_mode,
                'ai_difficulty': self.ai_difficulty
            }
            
            debug_log(f"게임 상태 검증 완료: {validation_result}", "INFO")
            return validation_result
            
        except Exception as e:
            debug_log(f"게임 상태 검증 실패: {e}", "ERROR")
            return None
    
    def set_game_mode(self, mode: str):
        """
        게임 모드 설정
        
        Args:
            mode (str): 게임 모드 ("2-Player" 또는 "AI Battle")
        """
        self.game_mode = mode
        self.restart_game()
        debug_log(f"게임 모드 변경: {mode}", "INFO")
    
    def cycle_ai_difficulty(self):
        """AI 난이도 순환 변경"""
        difficulties = ["Easy", "Medium", "Hard", "Expert"]
        current_index = difficulties.index(self.ai_difficulty)
        next_index = (current_index + 1) % len(difficulties)
        self.ai_difficulty = difficulties[next_index]
        self.ai.set_difficulty(self.ai_difficulty)
        self.sound_manager.play_click()
        debug_log(f"AI 난이도 변경: {self.ai_difficulty}", "INFO")
    
    def restart_game(self):
        """게임 재시작"""
        self.board.reset()
        self.game_stats.start_new_game(self.game_mode)
        self.sound_manager.play_click()
        self.ai_thinking = False
        debug_log("게임 재시작", "INFO")
    
    def update_fps(self):
        """FPS 계산 및 업데이트"""
        self.frame_count += 1
        current_time = time.time()
        
        if current_time - self.fps_start_time >= 1.0:
            self.last_fps = self.frame_count / (current_time - self.fps_start_time)
            self.frame_count = 0
            self.fps_start_time = current_time
            
            if self.debug_mode and self.last_fps < 30:
                debug_log(f"FPS 낮음: {self.last_fps:.1f}", "WARNING")
    
    def update(self):
        """게임 상태 업데이트"""
        try:
            # FPS 업데이트
            self.update_fps()
            
            # 애니메이션 시간 업데이트
            delta_time = self.clock.get_time() / 1000.0  # 초 단위로 변환
            self.renderer.update_animation_time(delta_time)
            
            # AI 차례 업데이트
            self.update_ai_turn()
            
            # 자동 테스트 모드 처리
            if self.auto_test_mode and self.test_moves and not self.ai_thinking:
                if len(self.test_moves) > 0:
                    move = self.test_moves.pop(0)
                    if self.board.place_stone(*move):
                        debug_log(f"자동 테스트 수: {move}", "DEBUG")
                        self.sound_manager.play_stone_place()
                        self.game_stats.record_move(self.board.get_current_player(), *move)
            
            # 게임 종료 조건 확인
            game_over, winner = self.board.get_game_status()
            if game_over and self.ui_mode != 'winner':
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
                self.ui_mode = 'winner'
                self.winner_info = {'winner': winner, 'is_draw': not winner}
                
                debug_log(f"게임 종료: 승자 {winner}", "INFO")
        except Exception as e:
            debug_log(f"게임 업데이트 오류: {e}", "ERROR")
            traceback.print_exc()
    
    def render(self):
        """게임 렌더링"""
        try:
            # 배경 그리기
            self.screen.fill(self.renderer.colors['background'])
            
            # 리플레이 모드인지 확인
            if self.ui_mode == 'replay':
                replay_board = self.game_history.get_replay_board()
                if replay_board:
                    # 리플레이 보드 렌더링
                    self.renderer.render_board(self.screen, replay_board)
                    # 리플레이 정보 표시
                    replay_info = self.game_history.get_replay_info()
                    if replay_info:
                        self.renderer.render_replay_info(self.screen, replay_info)
                else:
                    # 일반 보드 렌더링
                    self.renderer.render_board(self.screen, self.board)
            elif self.ui_mode == 'winner' and self.winner_info:
                self.renderer.render_winner_popup(self.screen, self.winner_info['winner'], self.game_mode)
            else:
                # 일반 보드 렌더링
                self.renderer.render_board(self.screen, self.board)
            
            # UI 렌더링
            self.renderer.render_ui(self.screen, self.board, self.game_mode, self.ai_difficulty, self.ai_thinking)
            
            # 디버그 정보 렌더링
            if self.debug_mode:
                self.render_debug_info()
            
            # 팝업/오버레이
            if self.ui_mode == 'winner' and self.winner_info and 'winner' in self.winner_info:
                self.renderer.render_winner_popup(self.screen, self.winner_info['winner'], self.game_mode)
            elif self.ui_mode == 'stats':
                self.renderer.render_stats_popup(self.screen, self.game_stats.get_stats_summary())
            elif self.ui_mode == 'history':
                self.renderer.render_history_popup(self.screen, self.game_history.get_recent_games(10))
            elif self.ui_mode == 'replay_select':
                self.renderer.render_replay_select_popup(self.screen, self.replay_select_list, self.replay_select_index)
            elif self.ui_mode == 'message':
                self.renderer.render_message_popup(self.screen, self.popup_message)
            
            # 화면 업데이트
            pygame.display.flip()
        except Exception as e:
            debug_log(f"렌더링 오류: {e}", "ERROR")
            traceback.print_exc()
    
    def render_debug_info(self):
        """디버그 정보 렌더링"""
        try:
            debug_font = pygame.font.Font(None, 24)
            debug_color = (255, 255, 0)  # 노란색
            
            # FPS 표시
            fps_text = f"FPS: {self.last_fps:.1f}"
            fps_surface = debug_font.render(fps_text, True, debug_color)
            self.screen.blit(fps_surface, (10, 10))
            
            # 게임 상태 표시
            game_over, winner = self.board.get_game_status()
            state_text = f"Game Over: {game_over}, Winner: {winner}"
            state_surface = debug_font.render(state_text, True, debug_color)
            self.screen.blit(state_surface, (10, 35))
            
            # AI 상태 표시
            ai_text = f"AI Thinking: {self.ai_thinking}, Mode: {self.game_mode}"
            ai_surface = debug_font.render(ai_text, True, debug_color)
            self.screen.blit(ai_surface, (10, 60))
            
            # 자동 테스트 상태 표시
            if self.auto_test_mode:
                test_text = f"Auto Test: {len(self.test_moves)} moves left"
                test_surface = debug_font.render(test_text, True, debug_color)
                self.screen.blit(test_surface, (10, 85))
        except Exception as e:
            debug_log(f"디버그 정보 렌더링 오류: {e}", "ERROR")
    
    def run(self):
        """게임 메인 루프"""
        debug_log("게임 메인 루프 시작", "INFO")
        
        try:
            while self.running:
                # 이벤트 처리
                self.handle_events()
                
                # 게임 상태 업데이트
                self.update()
                
                # 렌더링
                self.render()
                
                # FPS 제한
                self.clock.tick(60)
        except Exception as e:
            debug_log(f"게임 메인 루프 오류: {e}", "ERROR")
            traceback.print_exc()
        finally:
            # 게임 종료
            debug_log("게임 종료", "INFO")
            pygame.quit()
    
    def get_game_state(self):
        """
        현재 게임 상태 반환
        
        Returns:
            dict: 게임 상태 정보
        """
        try:
            game_over, winner = self.board.get_game_status()
            return {
                'game_mode': self.game_mode,
                'current_player': self.board.get_current_player(),
                'game_over': game_over,
                'winner': winner,
                'board_state': self.board.get_board_state().tolist(),
                'debug_mode': self.debug_mode,
                'auto_test_mode': self.auto_test_mode,
                'fps': self.last_fps
            }
        except Exception as e:
            debug_log(f"게임 상태 반환 오류: {e}", "ERROR")
            return None 