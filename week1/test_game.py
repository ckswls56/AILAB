#!/usr/bin/env python3
"""
3D 오목 게임 자동화 테스트 스크립트
"""

import sys
import time
import pygame
import numpy as np
from typing import List, Tuple, Dict
from game import Game
from board import Board
from ai import AI
from utils import debug_log


class GameTester:
    """게임 자동화 테스트 클래스"""
    
    def __init__(self):
        """테스트 초기화"""
        self.test_results = []
        self.passed_tests = 0
        self.failed_tests = 0
        
    def run_all_tests(self):
        """모든 테스트 실행"""
        debug_log("=== 게임 테스트 시작 ===", "INFO")
        
        # 기본 기능 테스트
        self.test_board_initialization()
        self.test_stone_placement()
        self.test_win_conditions()
        self.test_ai_functionality()
        self.test_game_modes()
        self.test_performance()
        
        # 결과 출력
        self.print_test_results()
        
    def test_board_initialization(self):
        """보드 초기화 테스트"""
        debug_log("보드 초기화 테스트 시작", "INFO")
        
        try:
            board = Board()
            
            # 보드 크기 확인
            assert board.size == 10, f"보드 크기가 잘못됨: {board.size}"
            
            # 초기 상태 확인
            board_state = board.get_board_state()
            assert board_state.shape == (10, 10), f"보드 상태 크기가 잘못됨: {board_state.shape}"
            
            # 모든 위치가 비어있는지 확인
            assert np.all(board_state == 0), "초기 보드가 비어있지 않음"
            
            # 현재 플레이어 확인
            assert board.get_current_player() == 1, f"초기 플레이어가 잘못됨: {board.get_current_player()}"
            
            self.record_test_result("보드 초기화", True, "성공")
            
        except Exception as e:
            self.record_test_result("보드 초기화", False, str(e))
    
    def test_stone_placement(self):
        """돌 배치 테스트"""
        debug_log("돌 배치 테스트 시작", "INFO")
        
        try:
            board = Board()
            
            # 유효한 돌 배치
            assert board.place_stone(4, 4), "중앙에 돌 배치 실패"
            assert board.board[4, 4] == 1, "돌이 올바르게 배치되지 않음"
            
            # 같은 위치에 중복 배치 시도
            assert not board.place_stone(4, 4), "중복 배치가 허용됨"
            
            # 플레이어 전환 확인
            assert board.get_current_player() == 2, "플레이어 전환 실패"
            
            # 두 번째 플레이어 돌 배치
            assert board.place_stone(5, 5), "두 번째 플레이어 돌 배치 실패"
            assert board.board[5, 5] == 2, "두 번째 플레이어 돌이 올바르게 배치되지 않음"
            
            self.record_test_result("돌 배치", True, "성공")
            
        except Exception as e:
            self.record_test_result("돌 배치", False, str(e))
    
    def test_win_conditions(self):
        """승리 조건 테스트"""
        debug_log("승리 조건 테스트 시작", "INFO")
        
        try:
            # 가로 승리 테스트
            board = Board()
            moves = [(4, 4), (4, 5), (4, 6), (4, 7), (4, 8)]
            
            for i, (row, col) in enumerate(moves):
                if i < 4:  # 5개 연속이 되기 전까지
                    assert board.place_stone(row, col), f"돌 배치 실패: ({row}, {col})"
                    game_over, winner = board.get_game_status()
                    assert not game_over, f"너무 일찍 게임 종료: {i+1}번째 수"
                
            # 5번째 수로 승리
            assert board.place_stone(moves[4][0], moves[4][1]), "승리 수 배치 실패"
            game_over, winner = board.get_game_status()
            assert game_over, "승리 조건이 감지되지 않음"
            assert winner == 1, f"승자가 잘못됨: {winner}"
            
            self.record_test_result("승리 조건", True, "성공")
            
        except Exception as e:
            self.record_test_result("승리 조건", False, str(e))
    
    def test_ai_functionality(self):
        """AI 기능 테스트"""
        debug_log("AI 기능 테스트 시작", "INFO")
        
        try:
            board = Board()
            ai = AI(player=2, difficulty="Easy")
            
            # AI가 수를 선택할 수 있는지 확인
            ai_move = ai.get_move(board)
            assert ai_move is not None, "AI가 수를 선택하지 못함"
            
            # AI 수가 유효한 범위 내에 있는지 확인
            row, col = ai_move
            assert 0 <= row < 10 and 0 <= col < 10, f"AI 수가 범위를 벗어남: ({row}, {col})"
            
            # AI 수가 빈 위치인지 확인
            assert board.board[row, col] == 0, f"AI가 이미 돌이 있는 위치를 선택: ({row}, {col})"
            
            # 난이도 변경 테스트
            ai.set_difficulty("Hard")
            assert ai.difficulty == "Hard", "AI 난이도 변경 실패"
            
            self.record_test_result("AI 기능", True, "성공")
            
        except Exception as e:
            self.record_test_result("AI 기능", False, str(e))
    
    def test_game_modes(self):
        """게임 모드 테스트"""
        debug_log("게임 모드 테스트 시작", "INFO")
        
        try:
            # 게임 인스턴스 생성
            game = Game(screen_width=800, screen_height=600)
            
            # 게임 모드 변경 테스트
            game.set_game_mode("AI Battle")
            assert game.game_mode == "AI Battle", "게임 모드 변경 실패"
            
            # AI 난이도 변경 테스트
            game.cycle_ai_difficulty()
            assert game.ai_difficulty in ["Easy", "Medium", "Hard", "Expert"], "AI 난이도가 유효하지 않음"
            
            # 게임 재시작 테스트
            game.restart_game()
            assert not game.board.game_over, "게임 재시작 후에도 게임이 종료됨"
            
            # 게임 상태 검증
            state = game.get_game_state()
            assert state is not None, "게임 상태 반환 실패"
            assert 'game_mode' in state, "게임 상태에 모드 정보가 없음"
            
            self.record_test_result("게임 모드", True, "성공")
            
        except Exception as e:
            self.record_test_result("게임 모드", False, str(e))
    
    def test_performance(self):
        """성능 테스트"""
        debug_log("성능 테스트 시작", "INFO")
        
        try:
            # AI 계산 시간 테스트
            board = Board()
            ai = AI(player=2, difficulty="Expert")
            
            start_time = time.time()
            ai_move = ai.get_move(board)
            end_time = time.time()
            
            calculation_time = end_time - start_time
            assert calculation_time < 5.0, f"AI 계산 시간이 너무 김: {calculation_time:.2f}초"
            
            # 보드 상태 업데이트 성능 테스트
            board = Board()
            start_time = time.time()
            
            for i in range(50):  # 50개의 돌 배치
                row, col = i // 10, i % 10
                board.place_stone(row, col)
                board.get_board_state()
            
            end_time = time.time()
            total_time = end_time - start_time
            
            assert total_time < 1.0, f"보드 업데이트 시간이 너무 김: {total_time:.2f}초"
            
            self.record_test_result("성능", True, f"AI: {calculation_time:.3f}s, Board: {total_time:.3f}s")
            
        except Exception as e:
            self.record_test_result("성능", False, str(e))
    
    def record_test_result(self, test_name: str, passed: bool, message: str):
        """테스트 결과 기록"""
        result = {
            'name': test_name,
            'passed': passed,
            'message': message,
            'timestamp': time.time()
        }
        
        self.test_results.append(result)
        
        if passed:
            self.passed_tests += 1
            debug_log(f"✅ {test_name}: {message}", "INFO")
        else:
            self.failed_tests += 1
            debug_log(f"❌ {test_name}: {message}", "ERROR")
    
    def print_test_results(self):
        """테스트 결과 출력"""
        total_tests = len(self.test_results)
        
        debug_log("=== 테스트 결과 ===", "INFO")
        debug_log(f"총 테스트: {total_tests}", "INFO")
        debug_log(f"성공: {self.passed_tests}", "INFO")
        debug_log(f"실패: {self.failed_tests}", "INFO")
        debug_log(f"성공률: {(self.passed_tests/total_tests)*100:.1f}%", "INFO")
        
        if self.failed_tests > 0:
            debug_log("=== 실패한 테스트 ===", "WARNING")
            for result in self.test_results:
                if not result['passed']:
                    debug_log(f"- {result['name']}: {result['message']}", "WARNING")
        
        debug_log("=== 테스트 완료 ===", "INFO")


def run_manual_tests():
    """수동 테스트 실행"""
    debug_log("수동 테스트 시작", "INFO")
    
    try:
        # 게임 인스턴스 생성
        game = Game(screen_width=800, screen_height=600)
        
        # 디버그 모드 활성화
        game.debug_mode = True
        
        # 자동 테스트 모드 활성화
        game.auto_test_mode = True
        
        debug_log("수동 테스트 설정 완료", "INFO")
        debug_log("게임을 실행하여 테스트를 확인하세요", "INFO")
        debug_log("F1: 디버그 모드, F2: 자동 테스트, F3: 상태 검증", "INFO")
        
        # 게임 실행
        game.run()
        
    except Exception as e:
        debug_log(f"수동 테스트 오류: {e}", "ERROR")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "manual":
        # 수동 테스트 모드
        run_manual_tests()
    else:
        # 자동 테스트 모드
        tester = GameTester()
        tester.run_all_tests() 