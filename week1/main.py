#!/usr/bin/env python3
"""
3D 오목 게임 메인 실행 파일
"""

import sys
import os

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from game import Game
    import pygame
    import numpy as np
except ImportError as e:
    print(f"Required libraries are not installed: {e}")
    print("Please install the required libraries with:")
    print("pip install pygame numpy")
    sys.exit(1)


def main():
    """Main function"""
    print("Starting 3D Gomoku Game...")
    print("=" * 50)
    print("Game Controls:")
    print("- Mouse Click: Place stone")
    print("- R key: Restart game")
    print("- ESC key: Exit game")
    print("- 1 key: 2-player mode")
    print("- 2 key: AI battle mode")
    print("=" * 50)
    
    try:
        # 게임 인스턴스 생성 및 실행
        game = Game(screen_width=1400, screen_height=900)
        game.run()
    except Exception as e:
        print(f"An error occurred while running the game: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 