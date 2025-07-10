# 🎮 3D Gomoku Game - AI Lab Week 1 Project

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![Pygame](https://img.shields.io/badge/Pygame-2.5+-green?style=for-the-badge&logo=python)
![NumPy](https://img.shields.io/badge/NumPy-1.24+-orange?style=for-the-badge&logo=numpy)
![AI](https://img.shields.io/badge/AI-Game-red?style=for-the-badge&logo=artificial-intelligence)

**3D 오목 게임 - AI 알고리즘과 게임 개발의 만남**

</div>

---

## 📋 프로젝트 개요

이 프로젝트는 **AI Lab Week 1**에서 개발한 3D 오목 게임입니다. Python과 Pygame을 사용하여 구현되었으며, 2인 플레이 모드와 AI 대전 모드를 지원합니다. 게임은 3D 시각 효과를 포함하여 현대적인 게임 경험을 제공합니다.

### 🎯 주요 특징
- **3D 시각 효과**: 입체적인 게임 보드와 돌 배치
- **AI 대전 모드**: 지능적인 AI 플레이어와 대전 가능
- **2인 플레이 모드**: 친구와 함께 즐기는 오목 게임
- **실시간 통계**: 게임 히스토리와 통계 관리
- **사운드 시스템**: 게임 효과음 지원

---

## 🚀 실행 가이드

### 1. 환경 설정

#### Python 버전 확인
```bash
python --version
# Python 3.8 이상 필요
```

#### 가상환경 생성 (권장)
```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 2. 의존성 설치

```bash
# 필요한 라이브러리 설치
pip install -r requirements.txt

# 또는 개별 설치
pip install pygame>=2.5.0 numpy>=1.24.0
```

### 3. 게임 실행

```bash
# 메인 게임 실행
python main.py
```

### 4. 게임 시작 화면

게임이 시작되면 다음과 같은 정보가 표시됩니다:

```
Starting 3D Gomoku Game...
==================================================
Game Controls:
- Mouse Click: Place stone
- R key: Restart game
- ESC key: Exit game
- 1 key: 2-player mode
- 2 key: AI battle mode
==================================================
```

---

## 🎮 게임 조작법

### 기본 조작
| 키/마우스 | 기능 |
|-----------|------|
| **마우스 클릭** | 돌 배치 |
| **R 키** | 게임 재시작 |
| **ESC 키** | 게임 종료 |
| **1 키** | 2인 플레이 모드 |
| **2 키** | AI 대전 모드 |

### 게임 규칙
- **보드 크기**: 10x10 격자
- **승리 조건**: 가로, 세로, 대각선으로 5개 돌을 연속 배치
- **턴**: 흑돌(검은색)부터 시작
- **무승부**: 보드가 가득 찬 경우

---

## 🏗️ 프로젝트 구조

```
week1/
├── main.py              # 메인 실행 파일
├── game.py              # 게임 로직 클래스 (575줄)
├── board.py             # 게임 보드 관리 (260줄)
├── ai.py               # AI 알고리즘 (475줄)
├── renderer.py         # 3D 렌더링 엔진 (643줄)
├── utils.py            # 유틸리티 함수 (395줄)
├── sound_manager.py    # 사운드 관리 (136줄)
├── game_history.py     # 게임 히스토리 관리 (290줄)
├── game_stats.py       # 게임 통계 관리 (245줄)
├── test_game.py        # 게임 테스트 (280줄)
├── requirements.txt    # 의존성 목록
├── README.md          # 프로젝트 문서
├── game_history.json  # 게임 히스토리 데이터
├── game_stats.json    # 게임 통계 데이터
└── game_debug.log     # 디버그 로그
```

---

## 🧠 AI 알고리즘

### AI 플레이어 특징
- **Minimax 알고리즘**: 최적의 수를 찾기 위한 탐색 알고리즘
- **알파-베타 가지치기**: 탐색 효율성 향상
- **평가 함수**: 보드 상태를 수치로 평가
- **깊이 제한**: 계산 시간과 성능의 균형

### AI 난이도
- **초급**: 2-3단계 깊이 탐색
- **중급**: 4-5단계 깊이 탐색
- **고급**: 6단계 이상 깊이 탐색

---

## 🎨 3D 렌더링 시스템

### 시각적 효과
- **입체적 보드**: 3D 격자 구조
- **그림자 효과**: 돌의 입체감 표현
- **애니메이션**: 부드러운 돌 배치 효과
- **색상 그라데이션**: 시각적 깊이감

### 렌더링 최적화
- **더블 버퍼링**: 깜빡임 방지
- **효율적 그리기**: 불필요한 렌더링 최소화
- **메모리 관리**: 자원 효율적 사용

---

## 📊 게임 통계 시스템

### 수집되는 데이터
- **게임 결과**: 승/패/무승부
- **플레이 시간**: 게임 진행 시간
- **수 순서**: 각 턴의 수 위치
- **AI 성능**: AI 승률 및 응답 시간

### 통계 파일
- `game_history.json`: 상세한 게임 기록
- `game_stats.json`: 요약 통계 데이터

---

## 🧪 테스트 시스템

### 테스트 실행
```bash
# 게임 테스트 실행
python test_game.py
```

### 테스트 범위
- **게임 로직**: 승리 조건, 무승부 조건
- **AI 알고리즘**: 정확성, 성능
- **사용자 입력**: 마우스 클릭, 키보드 입력
- **렌더링**: 화면 출력, 애니메이션

---

## 🛠️ 개발 환경

### 필수 요구사항
- **Python**: 3.8 이상
- **Pygame**: 2.5.0 이상
- **NumPy**: 1.24.0 이상
- **운영체제**: Windows, macOS, Linux

### 권장 사양
- **CPU**: Intel i3 이상 또는 동급 AMD
- **메모리**: 4GB RAM 이상
- **그래픽**: 기본 그래픽 카드
- **해상도**: 1024x768 이상

---

## 🐛 문제 해결

### 일반적인 문제

#### 1. Pygame 설치 오류
```bash
# Windows
pip install pygame --pre

# macOS
brew install pkg-config sdl2 sdl2_image sdl2_mixer sdl2_ttf portmidi
pip install pygame
```

#### 2. 게임 실행 시 오류
```bash
# 의존성 재설치
pip uninstall pygame numpy
pip install -r requirements.txt
```

#### 3. 성능 문제
- 게임 해상도 조정
- AI 탐색 깊이 감소
- 불필요한 프로그램 종료

### 디버그 모드
```bash
# 디버그 로그 활성화
python main.py --debug
```

---

## 📈 성능 최적화

### 최적화 기법
- **알고리즘 개선**: AI 탐색 효율성 향상
- **메모리 관리**: 불필요한 객체 생성 최소화
- **렌더링 최적화**: 화면 업데이트 최적화
- **입력 처리**: 이벤트 처리 효율성 향상

---

## 🤝 기여 가이드라인

### 코드 스타일
- **PEP 8**: Python 코딩 스타일 준수
- **주석**: 함수와 클래스에 상세한 주석
- **변수명**: 명확하고 의미있는 변수명 사용

### 기능 추가
1. Fork 저장소
2. 기능 브랜치 생성
3. 코드 작성 및 테스트
4. Pull Request 생성

---

## 📄 라이선스

이 프로젝트는 교육 목적으로 제작되었습니다.

---

## 📞 문의 및 지원

- **개발자**: ckswls56
- **이메일**: skxkswls@gmail.com
- **GitHub**: [https://github.com/ckswls56/AILAB](https://github.com/ckswls56/AILAB)

---

<div align="center">

**🎮 즐거운 3D 오목 게임을 즐겨보세요!**  
**🤖 AI와의 대전도 도전해보세요!**

</div> 