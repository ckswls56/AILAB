"""
Game Statistics Class
Tracks and manages game statistics and history.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional


class GameStats:
    """Game statistics and history tracker"""
    
    def __init__(self, stats_file: str = "game_stats.json"):
        """
        Initialize game statistics
        
        Args:
            stats_file (str): File to save statistics
        """
        self.stats_file = stats_file
        self.stats = self.load_stats()
        
        # Current game stats
        self.current_game = {
            'start_time': None,
            'moves': [],
            'winner': None,
            'game_mode': None,
            'duration': 0
        }
    
    def load_stats(self) -> Dict:
        """
        Load statistics from file
        
        Returns:
            Dict: Loaded statistics
        """
        default_stats = {
            'total_games': 0,
            'games_won': {'black': 0, 'white': 0, 'draw': 0},
            'game_modes': {'2-Player': 0, 'AI Battle': 0},
            'average_game_duration': 0,
            'total_moves': 0,
            'longest_game': 0,
            'shortest_game': float('inf'),
            'game_history': [],
            'ai_performance': {'wins': 0, 'losses': 0, 'draws': 0}
        }
        
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return default_stats
        else:
            return default_stats
    
    def save_stats(self):
        """Save statistics to file"""
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save stats: {e}")
    
    def start_new_game(self, game_mode: str):
        """
        Start tracking a new game
        
        Args:
            game_mode (str): Game mode (2-Player or AI Battle)
        """
        self.current_game = {
            'start_time': datetime.now(),
            'moves': [],
            'winner': None,
            'game_mode': game_mode,
            'duration': 0
        }
    
    def record_move(self, player: int, row: int, col: int):
        """
        Record a move in the current game
        
        Args:
            player (int): Player number (1: black, 2: white)
            row (int): Row position
            col (int): Column position
        """
        move = {
            'player': player,
            'position': (row, col),
            'timestamp': datetime.now().isoformat()
        }
        self.current_game['moves'].append(move)
    
    def end_game(self, winner: Optional[int], game_over: bool):
        """
        End the current game and update statistics
        
        Args:
            winner (Optional[int]): Winner (1: black, 2: white, None: draw)
            game_over (bool): Whether the game ended normally
        """
        if not game_over:
            return
        
        # Calculate game duration
        if self.current_game['start_time']:
            duration = (datetime.now() - self.current_game['start_time']).total_seconds()
            self.current_game['duration'] = duration
        
        # Update winner
        if winner:
            self.current_game['winner'] = winner
            winner_name = 'black' if winner == 1 else 'white'
        else:
            self.current_game['winner'] = None
            winner_name = 'draw'
        
        # Update statistics
        self.stats['total_games'] += 1
        self.stats['games_won'][winner_name] += 1
        self.stats['game_modes'][self.current_game['game_mode']] += 1
        self.stats['total_moves'] += len(self.current_game['moves'])
        
        # Update duration statistics
        duration = self.current_game['duration']
        if duration > 0:
            # Update average duration
            total_duration = self.stats['average_game_duration'] * (self.stats['total_games'] - 1) + duration
            self.stats['average_game_duration'] = total_duration / self.stats['total_games']
            
            # Update longest/shortest game
            self.stats['longest_game'] = max(self.stats['longest_game'], duration)
            if self.stats['shortest_game'] == float('inf'):
                self.stats['shortest_game'] = duration
            else:
                self.stats['shortest_game'] = min(self.stats['shortest_game'], duration)
        
        # Update AI performance if AI Battle mode
        if self.current_game['game_mode'] == 'AI Battle':
            if winner == 2:  # AI wins
                self.stats['ai_performance']['wins'] += 1
            elif winner == 1:  # Human wins
                self.stats['ai_performance']['losses'] += 1
            else:  # Draw
                self.stats['ai_performance']['draws'] += 1
        
        # Add to game history
        game_record = {
            'date': datetime.now().isoformat(),
            'mode': self.current_game['game_mode'],
            'winner': winner_name,
            'duration': duration,
            'moves': len(self.current_game['moves']),
            'moves_detail': self.current_game['moves']
        }
        
        self.stats['game_history'].append(game_record)
        
        # Keep only last 50 games in history
        if len(self.stats['game_history']) > 50:
            self.stats['game_history'] = self.stats['game_history'][-50:]
        
        # Save statistics
        self.save_stats()
    
    def get_stats_summary(self) -> Dict:
        """
        Get a summary of game statistics
        
        Returns:
            Dict: Statistics summary
        """
        total_games = self.stats['total_games']
        if total_games == 0:
            return {
                'total_games': 0,
                'win_rate': {'black': 0, 'white': 0, 'draw': 0},
                'average_duration': 0,
                'average_moves': 0,
                'ai_performance': {'wins': 0, 'losses': 0, 'draws': 0, 'win_rate': 0}
            }
        
        # Calculate win rates
        win_rate = {}
        for player, wins in self.stats['games_won'].items():
            win_rate[player] = (wins / total_games) * 100
        
        # Calculate AI performance
        ai_total = (self.stats['ai_performance']['wins'] + 
                   self.stats['ai_performance']['losses'] + 
                   self.stats['ai_performance']['draws'])
        
        ai_win_rate = 0
        if ai_total > 0:
            ai_win_rate = (self.stats['ai_performance']['wins'] / ai_total) * 100
        
        return {
            'total_games': total_games,
            'win_rate': win_rate,
            'average_duration': self.stats['average_game_duration'],
            'average_moves': self.stats['total_moves'] / total_games,
            'longest_game': self.stats['longest_game'],
            'shortest_game': self.stats['shortest_game'] if self.stats['shortest_game'] != float('inf') else 0,
            'game_modes': self.stats['game_modes'],
            'ai_performance': {
                'wins': self.stats['ai_performance']['wins'],
                'losses': self.stats['ai_performance']['losses'],
                'draws': self.stats['ai_performance']['draws'],
                'win_rate': ai_win_rate
            }
        }
    
    def get_recent_games(self, count: int = 10) -> List[Dict]:
        """
        Get recent game history
        
        Args:
            count (int): Number of recent games to return
            
        Returns:
            List[Dict]: Recent games
        """
        return self.stats['game_history'][-count:]
    
    def reset_stats(self):
        """Reset all statistics"""
        self.stats = {
            'total_games': 0,
            'games_won': {'black': 0, 'white': 0, 'draw': 0},
            'game_modes': {'2-Player': 0, 'AI Battle': 0},
            'average_game_duration': 0,
            'total_moves': 0,
            'longest_game': 0,
            'shortest_game': float('inf'),
            'game_history': [],
            'ai_performance': {'wins': 0, 'losses': 0, 'draws': 0}
        }
        self.save_stats() 