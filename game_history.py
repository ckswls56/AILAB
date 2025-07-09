"""
Game History and Replay Class
Manages game history and replay functionality.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from board import Board


class GameHistory:
    """Game history and replay manager"""
    
    def __init__(self, history_file: str = "game_history.json"):
        """
        Initialize game history
        
        Args:
            history_file (str): File to save game history
        """
        self.history_file = history_file
        self.history = self.load_history()
        self.current_replay = None
        self.replay_index = 0
        self.is_replaying = False
    
    def load_history(self) -> List[Dict]:
        """
        Load game history from file
        
        Returns:
            List[Dict]: Loaded game history
        """
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
    
    def save_history(self):
        """Save game history to file"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save history: {e}")
    
    def add_game(self, game_data: Dict):
        """
        Add a completed game to history
        
        Args:
            game_data (Dict): Game data to add
        """
        game_record = {
            'id': len(self.history) + 1,
            'timestamp': datetime.now().isoformat(),
            'game_mode': game_data.get('game_mode', 'Unknown'),
            'winner': game_data.get('winner', None),
            'is_draw': game_data.get('is_draw', False),
            'duration': game_data.get('duration', 0),
            'total_moves': game_data.get('total_moves', 0),
            'moves': game_data.get('moves', []),
            'board_size': game_data.get('board_size', 10),
            'ai_performance': game_data.get('ai_performance', {})
        }
        
        self.history.append(game_record)
        self.save_history()
    
    def get_recent_games(self, count: int = 10) -> List[Dict]:
        """
        Get recent games
        
        Args:
            count (int): Number of recent games to return
            
        Returns:
            List[Dict]: Recent games
        """
        return self.history[-count:] if self.history else []
    
    def get_game_by_id(self, game_id: int) -> Optional[Dict]:
        """
        Get game by ID
        
        Args:
            game_id (int): Game ID
            
        Returns:
            Optional[Dict]: Game data or None
        """
        for game in self.history:
            if game['id'] == game_id:
                return game
        return None
    
    def start_replay(self, game_id: int) -> bool:
        """
        Start replaying a specific game
        
        Args:
            game_id (int): Game ID to replay
            
        Returns:
            bool: Success status
        """
        game = self.get_game_by_id(game_id)
        if not game:
            return False
        
        self.current_replay = game
        self.replay_index = 0
        self.is_replaying = True
        return True
    
    def stop_replay(self):
        """Stop current replay"""
        self.current_replay = None
        self.replay_index = 0
        self.is_replaying = False
    
    def get_replay_board(self) -> Optional[Board]:
        """
        Get current replay board state
        
        Returns:
            Optional[Board]: Current board state or None
        """
        if not self.is_replaying or not self.current_replay:
            return None
        
        # Create a new board
        board = Board(size=self.current_replay['board_size'])
        
        # Apply moves up to current replay index
        moves = self.current_replay['moves']
        for i in range(min(self.replay_index, len(moves))):
            move = moves[i]
            row, col = move['position']
            player = move['player']
            board.board[row, col] = player
        
        return board
    
    def next_move(self) -> bool:
        """
        Go to next move in replay
        
        Returns:
            bool: True if there are more moves
        """
        if not self.is_replaying or not self.current_replay:
            return False
        
        if self.replay_index < len(self.current_replay['moves']):
            self.replay_index += 1
            return True
        return False
    
    def previous_move(self) -> bool:
        """
        Go to previous move in replay
        
        Returns:
            bool: True if there are previous moves
        """
        if not self.is_replaying or not self.current_replay:
            return False
        
        if self.replay_index > 0:
            self.replay_index -= 1
            return True
        return False
    
    def get_replay_info(self) -> Optional[Dict]:
        """
        Get current replay information
        
        Returns:
            Optional[Dict]: Replay info or None
        """
        if not self.is_replaying or not self.current_replay:
            return None
        
        return {
            'game_id': self.current_replay['id'],
            'current_move': self.replay_index,
            'total_moves': len(self.current_replay['moves']),
            'game_mode': self.current_replay['game_mode'],
            'winner': self.current_replay['winner'],
            'is_draw': self.current_replay['is_draw']
        }
    
    def export_game(self, game_id: int, filename: str) -> bool:
        """
        Export a game to a separate file
        
        Args:
            game_id (int): Game ID to export
            filename (str): Output filename
            
        Returns:
            bool: Success status
        """
        game = self.get_game_by_id(game_id)
        if not game:
            return False
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(game, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Failed to export game: {e}")
            return False
    
    def import_game(self, filename: str) -> bool:
        """
        Import a game from file
        
        Args:
            filename (str): Input filename
            
        Returns:
            bool: Success status
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                game_data = json.load(f)
            
            # Validate game data
            required_fields = ['game_mode', 'moves', 'board_size']
            if not all(field in game_data for field in required_fields):
                return False
            
            # Add to history
            game_data['id'] = len(self.history) + 1
            game_data['timestamp'] = datetime.now().isoformat()
            self.history.append(game_data)
            self.save_history()
            return True
            
        except Exception as e:
            print(f"Failed to import game: {e}")
            return False
    
    def get_statistics(self) -> Dict:
        """
        Get history statistics
        
        Returns:
            Dict: History statistics
        """
        if not self.history:
            return {
                'total_games': 0,
                'average_moves': 0,
                'average_duration': 0,
                'win_rates': {'black': 0, 'white': 0, 'draw': 0}
            }
        
        total_games = len(self.history)
        total_moves = sum(game['total_moves'] for game in self.history)
        total_duration = sum(game['duration'] for game in self.history)
        
        # Calculate win rates
        wins = {'black': 0, 'white': 0, 'draw': 0}
        for game in self.history:
            if game['is_draw']:
                wins['draw'] += 1
            elif game['winner'] == 1:
                wins['black'] += 1
            elif game['winner'] == 2:
                wins['white'] += 1
        
        return {
            'total_games': total_games,
            'average_moves': total_moves / total_games if total_games > 0 else 0,
            'average_duration': total_duration / total_games if total_games > 0 else 0,
            'win_rates': {
                'black': (wins['black'] / total_games) * 100 if total_games > 0 else 0,
                'white': (wins['white'] / total_games) * 100 if total_games > 0 else 0,
                'draw': (wins['draw'] / total_games) * 100 if total_games > 0 else 0
            }
        } 