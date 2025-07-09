"""
유틸리티 함수들
게임에서 사용하는 다양한 헬퍼 함수들을 포함합니다.
"""

import pygame
import math
import logging
import time
from typing import Tuple, Optional

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('game_debug.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def debug_log(message: str, level: str = "INFO"):
    """
    디버그 로그 출력
    
    Args:
        message (str): 로그 메시지
        level (str): 로그 레벨 ("DEBUG", "INFO", "WARNING", "ERROR")
    """
    if level == "DEBUG":
        logger.debug(message)
    elif level == "INFO":
        logger.info(message)
    elif level == "WARNING":
        logger.warning(message)
    elif level == "ERROR":
        logger.error(message)


def performance_timer(func):
    """
    성능 측정 데코레이터
    
    Args:
        func: 측정할 함수
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        
        if execution_time > 0.1:  # 0.1초 이상 걸리는 함수만 로그
            debug_log(f"{func.__name__} 실행 시간: {execution_time:.3f}초", "WARNING")
        
        return result
    return wrapper


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


@performance_timer
def create_3d_effect(surface: pygame.Surface, rect: pygame.Rect, 
                     color: Tuple[int, int, int], depth: int = 5):
    """
    고급 3D 효과를 위한 그림자와 하이라이트 생성
    
    Args:
        surface (pygame.Surface): 그릴 서피스
        rect (pygame.Rect): 그릴 영역
        color (Tuple[int, int, int]): 기본 색상
        depth (int): 3D 효과 깊이
    """
    # 다층 그림자 효과 (더 현실적인 그림자)
    for i in range(depth, 0, -1):
        shadow_alpha = max(0, 100 - i * 20)  # 거리에 따른 투명도
        shadow_color = tuple(max(0, c - 30 - i * 5) for c in color)
        
        shadow_rect = rect.copy()
        shadow_rect.x += i
        shadow_rect.y += i
        
        # 반투명 그림자 서피스 생성
        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        shadow_surface.fill((*shadow_color, shadow_alpha))
        surface.blit(shadow_surface, shadow_rect)
    
    # 메인 오브젝트 그리기
    pygame.draw.rect(surface, color, rect)
    
    # 다층 하이라이트 효과
    for i in range(1, min(4, depth)):
        highlight_alpha = max(0, 80 - i * 25)
        highlight_color = tuple(min(255, c + 20 + i * 5) for c in color)
        
        highlight_rect = rect.copy()
        highlight_rect.width = i * 2
        highlight_rect.height = i * 2
        
        # 반투명 하이라이트 서피스 생성
        highlight_surface = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
        highlight_surface.fill((*highlight_color, highlight_alpha))
        surface.blit(highlight_surface, highlight_rect)


@performance_timer
def create_stone_3d_effect(surface: pygame.Surface, center: Tuple[int, int], 
                          radius: int, color: Tuple[int, int, int], is_white: bool = False):
    """
    돌의 고급 3D 효과 생성
    
    Args:
        surface (pygame.Surface): 그릴 서피스
        center (Tuple[int, int]): 돌의 중심점
        radius (int): 돌의 반지름
        color (Tuple[int, int, int]): 돌의 기본 색상
        is_white (bool): 흰돌 여부
    """
    x, y = center
    
    # 다층 그림자 효과
    for i in range(3, 0, -1):
        shadow_alpha = max(0, 120 - i * 40)
        shadow_color = tuple(max(0, c - 40 - i * 10) for c in color)
        
        shadow_surface = pygame.Surface((radius * 2 + 6, radius * 2 + 6), pygame.SRCALPHA)
        pygame.draw.circle(shadow_surface, (*shadow_color, shadow_alpha), 
                          (radius + 3, radius + 3), radius)
        surface.blit(shadow_surface, (x - radius - 3 + i, y - radius - 3 + i))
    
    # 메인 돌 그리기
    pygame.draw.circle(surface, color, (x, y), radius)
    
    # 하이라이트 효과
    if is_white:
        # 흰돌의 경우 더 강한 하이라이트
        highlight_radius = radius // 2
        highlight_pos = (x - highlight_radius // 2, y - highlight_radius // 2)
        pygame.draw.circle(surface, (240, 240, 240), highlight_pos, highlight_radius)
        
        # 추가 하이라이트
        small_highlight_radius = radius // 4
        small_highlight_pos = (x - small_highlight_radius // 2, y - small_highlight_radius // 2)
        pygame.draw.circle(surface, (255, 255, 255), small_highlight_pos, small_highlight_radius)
    else:
        # 검은돌의 경우 미묘한 하이라이트
        highlight_radius = radius // 3
        highlight_pos = (x - highlight_radius // 2, y - highlight_radius // 2)
        pygame.draw.circle(surface, (50, 50, 50), highlight_pos, highlight_radius)


def create_animated_3d_effect(surface: pygame.Surface, rect: pygame.Rect, 
                             color: Tuple[int, int, int], time: float, 
                             animation_type: str = "pulse"):
    """
    애니메이션 3D 효과 생성
    
    Args:
        surface (pygame.Surface): 그릴 서피스
        rect (pygame.Rect): 그릴 영역
        color (Tuple[int, int, int]): 기본 색상
        time (float): 애니메이션 시간 (초)
        animation_type (str): 애니메이션 타입 ("pulse", "glow", "wave")
    """
    if animation_type == "pulse":
        # 펄스 효과
        pulse_factor = 1.0 + 0.1 * math.sin(time * 5)
        pulse_rect = rect.copy()
        pulse_rect.width = int(rect.width * pulse_factor)
        pulse_rect.height = int(rect.height * pulse_factor)
        pulse_rect.center = rect.center
        
        create_3d_effect(surface, pulse_rect, color, depth=3)
        
    elif animation_type == "glow":
        # 글로우 효과
        glow_intensity = 0.5 + 0.5 * math.sin(time * 3)
        glow_color = tuple(min(255, int(c + 50 * glow_intensity)) for c in color)
        
        # 글로우 서피스 생성
        glow_surface = pygame.Surface((rect.width + 20, rect.height + 20), pygame.SRCALPHA)
        glow_alpha = int(100 * glow_intensity)
        pygame.draw.rect(glow_surface, (*glow_color, glow_alpha), 
                        (10, 10, rect.width, rect.height), border_radius=10)
        surface.blit(glow_surface, (rect.x - 10, rect.y - 10))
        
        create_3d_effect(surface, rect, color, depth=3)
        
    elif animation_type == "wave":
        # 웨이브 효과
        wave_offset = 5 * math.sin(time * 4)
        wave_rect = rect.copy()
        wave_rect.y += int(wave_offset)
        
        create_3d_effect(surface, wave_rect, color, depth=3)


def draw_text_with_shadow(surface: pygame.Surface, text: str, font: pygame.font.Font,
                         color: Tuple[int, int, int], pos: Tuple[int, int], 
                         shadow_offset: int = 2, shadow_color: Optional[Tuple[int, int, int]] = None):
    """
    고급 그림자가 있는 텍스트 그리기
    
    Args:
        surface (pygame.Surface): 그릴 서피스
        text (str): 표시할 텍스트
        font (pygame.font.Font): 폰트
        color (Tuple[int, int, int]): 텍스트 색상
        pos (Tuple[int, int]): 위치 (x, y)
        shadow_offset (int): 그림자 오프셋
        shadow_color (Optional[Tuple[int, int, int]]): 그림자 색상 (None이면 자동 계산)
    """
    if shadow_color is None:
        shadow_color = (0, 0, 0)
    
    # 다층 그림자 효과
    for i in range(shadow_offset, 0, -1):
        shadow_alpha = max(0, 150 - i * 50)
        shadow_surface = font.render(text, True, shadow_color)
        shadow_surface.set_alpha(shadow_alpha)
        shadow_pos = (pos[0] + i, pos[1] + i)
        surface.blit(shadow_surface, shadow_pos)
    
    # 메인 텍스트
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, pos)


def draw_text_with_glow(surface: pygame.Surface, text: str, font: pygame.font.Font,
                       color: Tuple[int, int, int], pos: Tuple[int, int], 
                       glow_intensity: float = 0.5):
    """
    글로우 효과가 있는 텍스트 그리기
    
    Args:
        surface (pygame.Surface): 그릴 서피스
        text (str): 표시할 텍스트
        font (pygame.font.Font): 폰트
        color (Tuple[int, int, int]): 텍스트 색상
        pos (Tuple[int, int]): 위치 (x, y)
        glow_intensity (float): 글로우 강도 (0.0 ~ 1.0)
    """
    # 글로우 효과
    glow_color = tuple(min(255, int(c + 100 * glow_intensity)) for c in color)
    
    # 글로우 텍스트 (여러 레이어)
    for i in range(3, 0, -1):
        glow_alpha = int(50 * glow_intensity * i / 3)
        glow_surface = font.render(text, True, glow_color)
        glow_surface.set_alpha(glow_alpha)
        glow_pos = (pos[0] + i, pos[1] + i)
        surface.blit(glow_surface, glow_pos)
    
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
    r = int(color1[0] + (color2[0] - color1[0]) * factor)
    g = int(color1[1] + (color2[1] - color1[1]) * factor)
    b = int(color1[2] + (color2[2] - color1[2]) * factor)
    return (r, g, b)


def create_gradient_surface(width: int, height: int, 
                          color1: Tuple[int, int, int], 
                          color2: Tuple[int, int, int],
                          direction: str = "vertical") -> pygame.Surface:
    """
    고급 그라데이션 서피스 생성
    
    Args:
        width (int): 너비
        height (int): 높이
        color1 (Tuple[int, int, int]): 시작 색상
        color2 (Tuple[int, int, int]): 끝 색상
        direction (str): 그라데이션 방향 ("vertical", "horizontal", "radial")
        
    Returns:
        pygame.Surface: 그라데이션 서피스
    """
    surface = pygame.Surface((width, height))
    
    if direction == "vertical":
        for y in range(height):
            factor = y / height
            color = interpolate_color(color1, color2, factor)
            pygame.draw.line(surface, color, (0, y), (width, y))
    
    elif direction == "horizontal":
        for x in range(width):
            factor = x / width
            color = interpolate_color(color1, color2, factor)
            pygame.draw.line(surface, color, (x, 0), (x, height))
    
    elif direction == "radial":
        center_x, center_y = width // 2, height // 2
        max_distance = math.sqrt(center_x**2 + center_y**2)
        
        for y in range(height):
            for x in range(width):
                distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                factor = min(1.0, distance / max_distance)
                color = interpolate_color(color1, color2, factor)
                surface.set_at((x, y), color)
    
    return surface


def create_particle_effect(surface: pygame.Surface, center: Tuple[int, int], 
                          color: Tuple[int, int, int], particle_count: int = 10, 
                          time: float = 0.0):
    """
    파티클 효과 생성
    
    Args:
        surface (pygame.Surface): 그릴 서피스
        center (Tuple[int, int]): 파티클 중심점
        color (Tuple[int, int, int]): 파티클 색상
        particle_count (int): 파티클 개수
        time (float): 애니메이션 시간
    """
    for i in range(particle_count):
        angle = (i / particle_count) * 2 * math.pi + time * 2
        distance = 20 + 10 * math.sin(time * 3 + i)
        
        x = center[0] + int(distance * math.cos(angle))
        y = center[1] + int(distance * math.sin(angle))
        
        particle_alpha = int(255 * (1.0 - time))
        particle_surface = pygame.Surface((4, 4), pygame.SRCALPHA)
        particle_surface.fill((*color, particle_alpha))
        surface.blit(particle_surface, (x - 2, y - 2)) 