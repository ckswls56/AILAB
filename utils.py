"""
유틸리티 함수들
게임에서 사용하는 다양한 헬퍼 함수들을 포함합니다.
"""

import pygame
from typing import Tuple, Optional


def screen_to_board_pos(screen_pos: Tuple[int, int], board_rect: pygame.Rect, 
                       cell_size: int) -> Optional[Tuple[int, int]]:
    """
    화면 좌표를 보드 좌표로 변환
    
    Args:
        screen_pos (Tuple[int, int]): 화면 좌표 (x, y)
        board_rect (pygame.Rect): 보드의 화면 영역
        cell_size (int): 셀 크기
        
    Returns:
        Optional[Tuple[int, int]]: 보드 좌표 (row, col) 또는 None
    """
    x, y = screen_pos
    
    # 보드 영역 내에 있는지 확인
    if not board_rect.collidepoint(x, y):
        return None
    
    # 보드 좌표 계산
    board_x = x - board_rect.x
    board_y = y - board_rect.y
    
    col = board_x // cell_size
    row = board_y // cell_size
    
    return row, col


def board_to_screen_pos(board_pos: Tuple[int, int], board_rect: pygame.Rect, 
                       cell_size: int) -> Tuple[int, int]:
    """
    보드 좌표를 화면 좌표로 변환
    
    Args:
        board_pos (Tuple[int, int]): 보드 좌표 (row, col)
        board_rect (pygame.Rect): 보드의 화면 영역
        cell_size (int): 셀 크기
        
    Returns:
        Tuple[int, int]: 화면 좌표 (x, y)
    """
    row, col = board_pos
    x = board_rect.x + col * cell_size + cell_size // 2
    y = board_rect.y + row * cell_size + cell_size // 2
    return x, y


def create_3d_effect(surface: pygame.Surface, rect: pygame.Rect, 
                     color: Tuple[int, int, int], depth: int = 3):
    """
    3D 효과를 위한 그림자와 하이라이트 생성
    
    Args:
        surface (pygame.Surface): 그릴 서피스
        rect (pygame.Rect): 그릴 영역
        color (Tuple[int, int, int]): 기본 색상
        depth (int): 3D 효과 깊이
    """
    # 그림자 효과 (어두운 색상)
    shadow_color = tuple(max(0, c - 50) for c in color)
    shadow_rect = rect.copy()
    shadow_rect.x += depth
    shadow_rect.y += depth
    pygame.draw.rect(surface, shadow_color, shadow_rect)
    
    # 하이라이트 효과 (밝은 색상)
    highlight_color = tuple(min(255, c + 30) for c in color)
    highlight_rect = rect.copy()
    highlight_rect.width = depth
    highlight_rect.height = depth
    pygame.draw.rect(surface, highlight_color, highlight_rect)
    
    # 기본 색상으로 그리기
    pygame.draw.rect(surface, color, rect)


def draw_text_with_shadow(surface: pygame.Surface, text: str, font: pygame.font.Font,
                         color: Tuple[int, int, int], pos: Tuple[int, int]):
    """
    그림자가 있는 텍스트 그리기
    
    Args:
        surface (pygame.Surface): 그릴 서피스
        text (str): 표시할 텍스트
        font (pygame.font.Font): 폰트
        color (Tuple[int, int, int]): 텍스트 색상
        pos (Tuple[int, int]): 위치 (x, y)
    """
    # 그림자 텍스트
    shadow_color = (0, 0, 0)
    shadow_surface = font.render(text, True, shadow_color)
    shadow_pos = (pos[0] + 2, pos[1] + 2)
    surface.blit(shadow_surface, shadow_pos)
    
    # 메인 텍스트
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, pos)


def interpolate_color(color1: Tuple[int, int, int], color2: Tuple[int, int, int], 
                     factor: float) -> Tuple[int, int, int]:
    """
    두 색상 사이를 보간
    
    Args:
        color1 (Tuple[int, int, int]): 첫 번째 색상
        color2 (Tuple[int, int, int]): 두 번째 색상
        factor (float): 보간 계수 (0.0 ~ 1.0)
        
    Returns:
        Tuple[int, int, int]: 보간된 색상
    """
    return tuple(int(c1 + (c2 - c1) * factor) for c1, c2 in zip(color1, color2))


def create_gradient_surface(width: int, height: int, 
                          color1: Tuple[int, int, int], 
                          color2: Tuple[int, int, int]) -> pygame.Surface:
    """
    그라데이션 서피스 생성
    
    Args:
        width (int): 너비
        height (int): 높이
        color1 (Tuple[int, int, int]): 시작 색상
        color2 (Tuple[int, int, int]): 끝 색상
        
    Returns:
        pygame.Surface: 그라데이션 서피스
    """
    surface = pygame.Surface((width, height))
    
    for y in range(height):
        factor = y / height
        color = interpolate_color(color1, color2, factor)
        pygame.draw.line(surface, color, (0, y), (width, y))
    
    return surface 