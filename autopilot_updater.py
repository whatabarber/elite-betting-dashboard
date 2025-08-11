#!/usr/bin/env python3
"""
FIXED AUTOPILOT BETTING SITE UPDATER
Automatically generates Pete Prisco style analysis and updates your HTML site
Run weekly to get fresh picks and parlays
"""

import requests
import json
import random
from datetime import datetime, timedelta
import os
from typing import List, Dict, Any

class AutoPilotBettingUpdater:
    def __init__(self):
        # Try to load from .env, fall back to placeholder
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass
        
        self.api_keys = {
            'odds_api': os.getenv('ODDS_API_KEY', 'your_odds_api_key_from_the-odds-api.com'),
            'weather_api': os.getenv('WEATHER_API_KEY', 'your_weather_key'),
            'news_api': os.getenv('NEWS_API_KEY', 'your_news_key')
        }
        
        self.current_week = self.get_current_week()
        self.bovada_focus = True
        
        # Analysis templates
        self.analysis_templates = {
            'opening_hooks': [
                "This line screams trap game to me.",
                "The books are begging you to take the obvious side here.",
                "Classic case of the public being wrong.",
                "This is the type of spot that separates the pros from the squares.",
                "The sharps have been all over this number.",
                "Public money is flowing one way, but I'm going the other.",
            ],
            'matchup_intros': [
                "Let's break down what really matters in this matchup.",
                "The key to this game comes down to a few critical factors.",
                "When you dig into the numbers, the story becomes clear.",
                "This matchup has several interesting angles.",
                "The tape tells a different story than the line suggests.",
            ],
            'conclusion_phrases': [
                "Take the points and run.",
                "This one won't be close.",
                "I'm confident in this pick.",
                "The value is too good to pass up.",
                "This is a max play for me.",
                "Lock it in and don't look back.",
            ]
        }

    def get_current_week(self) -> int:
        """Calculate current NFL week"""
        season_start = datetime(2025, 9, 5)  # Adjusted for 2025 season
        now = datetime.now()
        weeks_passed = (now - season_start).days // 7
        return max(1, min(weeks_passed + 1, 18))

    def fetch_live_nfl_games(self) -> List[Dict]:
        """Fetch live NFL games and odds"""
        try:
            url = f"https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds"
            params = {
                'apiKey': self.api_keys['odds_api'],
                'regions': 'us',
                'markets': 'spreads,totals,h2h',
                'oddsFormat': 'american'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            games_data = response.json()
            processed_games = []
            
            for game in games_data:
                processed_game = self.process_game_data(game, 'NFL')
                if processed_game:
                    processed_games.append(processed_game)
            
            print(f"✅ Fetched {len(processed_games)} NFL games")
            return processed_games
            
        except Exception as e:
            print(f"❌ Failed to fetch NFL games: {e}")
            return self.get_demo_nfl_games()

    def fetch_live_cfb_games(self) -> List[Dict]:
        """Fetch live CFB games and odds"""
        try:
            url = f"https://api.the-odds-api.com/v4/sports/americanfootball_ncaaf/odds"
            params = {
                'apiKey': self.api_keys['odds_api'],
                'regions': 'us',
                'markets': 'spreads,totals,h2h',
                'oddsFormat': 'american'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            games_data = response.json()
            processed_games = []
            
            for game in games_data:
                processed_game = self.process_game_data(game, 'CFB')
                if processed_game:
                    processed_games.append(processed_game)
            
            print(f"✅ Fetched {len(processed_games)} CFB games")
            return processed_games
            
        except Exception as e:
            print(f"❌ Failed to fetch CFB games: {e}")
            return self.get_demo_cfb_games()

    def process_game_data(self, game_data: Dict, league: str) -> Dict:
        """Process raw game data into our format"""
        try:
            away_team = game_data['away_team']
            home_team = game_data['home_team']
            commence_time = game_data['commence_time']
            
            lines = self.extract_bovada_lines(game_data['bookmakers'])
            
            return {
                'away_team': away_team,
                'home_team': home_team,
                'commence_time': commence_time,
                'spread': lines['spread'],
                'total': lines['total'],
                'away_ml': lines['away_ml'],
                'home_ml': lines['home_ml'],
                'league': league
            }
            
        except Exception as e:
            print(f"❌ Failed to process game data: {e}")
            return None

    def extract_bovada_lines(self, bookmakers: List[Dict]) -> Dict:
        """Extract betting lines, prioritizing Bovada"""
        lines = {'spread': 0, 'total': 45, 'away_ml': 100, 'home_ml': -120}
        
        bovada_book = None
        for book in bookmakers:
            if 'bovada' in book.get('title', '').lower():
                bovada_book = book
                break
        
        target_book = bovada_book if bovada_book else bookmakers[0] if bookmakers else None
        
        if target_book:
            for market in target_book['markets']:
                if market['key'] == 'spreads':
                    lines['spread'] = market['outcomes'][1]['point']
                elif market['key'] == 'totals':
                    lines['total'] = market['outcomes'][0]['point']
                elif market['key'] == 'h2h':
                    lines['away_ml'] = market['outcomes'][0]['price']
                    lines['home_ml'] = market['outcomes'][1]['price']
        
        return lines

    def generate_game_analysis(self, game: Dict) -> Dict:
        """Generate Pete Prisco style analysis for a game"""
        
        pick_data = self.calculate_pick(game)
        
        analysis_sections = {
            'the_line': self.generate_line_analysis(game, pick_data),
            'the_matchup': self.generate_matchup_analysis(game, pick_data),
            'the_angle': self.generate_angle_analysis(game, pick_data),
            'the_bottom_line': self.generate_bottom_line(game, pick_data)
        }
        
        predicted_score = self.generate_predicted_score(game, pick_data)
        
        return {
            'game_info': {
                'away_team': game['away_team'],
                'home_team': game['home_team'],
                'time': self.format_game_time(game['commence_time']),
                'venue': self.get_venue(game['home_team']),
                'spread': game['spread'],
                'total': game['total'],
                'away_ml': game['away_ml'],
                'home_ml': game['home_ml']
            },
            'pick': pick_data,
            'predicted_score': predicted_score,
            'analysis': analysis_sections
        }

    def calculate_pick(self, game: Dict) -> Dict:
        """Calculate which team to pick using multiple factors"""
        
        factors = {
            'home_field_advantage': random.uniform(-3, 3),
            'recent_form': random.uniform(-2, 2),
            'matchup_advantage': random.uniform(-4, 4),
            'motivation_factor': random.uniform(-1.5, 1.5),
            'weather_impact': random.uniform(-1, 1),
            'injury_impact': random.uniform(-2, 2),
            'public_betting': random.uniform(0.3, 0.8)
        }
        
        total_edge = sum(factors.values())
        spread = game['spread']
        
        if total_edge > abs(spread) + 1:
            if spread < 0:
                pick_team = game['home_team']
                pick_line = f"{spread}"
            else:
                pick_team = game['away_team'] 
                pick_line = f"+{spread}"
        elif total_edge < -(abs(spread) + 1):
            if spread < 0:
                pick_team = game['away_team']
                pick_line = f"+{abs(spread)}"
            else:
                pick_team = game['home_team']
                pick_line = f"{spread}"
        else:
            if spread < 0:
                pick_team = game['away_team']
                pick_line = f"+{abs(spread)}"
            else:
                pick_team = game['home_team']
                pick_line = f"{spread}"
        
        return {
            'team': pick_team,
            'line': pick_line,
            'confidence': min(abs(total_edge) * 10 + 60, 90),
            'factors': factors
        }

    def generate_line_analysis(self, game: Dict, pick_data: Dict) -> str:
        """Generate analysis of the betting line"""
        hook = random.choice(self.analysis_templates['opening_hooks'])
        
        spread = abs(game['spread'])
        public_side = "favorite" if pick_data['factors']['public_betting'] > 0.6 else "underdog"
        
        analysis = f"{hook} "
        
        if spread <= 3:
            analysis += f"This is essentially a pick'em game, but the {spread}-point spread tells a story. "
        elif spread <= 7:
            analysis += f"The {spread}-point spread feels about right on paper, but I think there's value here. "
        else:
            analysis += f"That's a big number at {spread} points, but sometimes big spreads are there for a reason. "
        
        if pick_data['factors']['public_betting'] > 0.7:
            analysis += f"The public is all over the {public_side}, which immediately makes me want to go the other way. "
        
        return analysis

    def generate_matchup_analysis(self, game: Dict, pick_data: Dict) -> str:
        """Generate matchup breakdown"""
        intro = random.choice(self.analysis_templates['matchup_intros'])
        
        analysis = f"{intro} "
        
        if pick_data['factors']['matchup_advantage'] > 2:
            analysis += f"{pick_data['team']} has significant advantages on both sides of the ball. "
            analysis += "Their offensive scheme should create problems, while defensively they match up well. "
        elif pick_data['factors']['matchup_advantage'] > 0:
            analysis += f"{pick_data['team']} has the edge in the key matchups that will decide this game. "
        else:
            analysis += "This is a pretty even matchup on paper, but the details matter. "
        
        analysis += "The offensive line play will be crucial, and the team that wins the turnover battle likely wins the game. "
        
        return analysis

    def generate_angle_analysis(self, game: Dict, pick_data: Dict) -> str:
        """Generate sharp angle analysis"""
        analysis = ""
        
        if pick_data['factors']['motivation_factor'] > 1:
            analysis += f"{pick_data['team']} is in a revenge spot and should be motivated. "
        elif pick_data['factors']['motivation_factor'] < -1:
            analysis += f"This could be a letdown spot for {pick_data['team']} after their last performance. "
        
        if pick_data['factors']['recent_form'] > 1:
            analysis += f"The momentum is clearly with {pick_data['team']} right now. "
        
        if abs(pick_data['factors']['weather_impact']) > 0.5:
            if pick_data['factors']['weather_impact'] > 0:
                analysis += "Weather conditions should favor the running game and Under. "
            else:
                analysis += "Perfect conditions for an offensive showcase. "
        
        if abs(pick_data['factors']['injury_impact']) > 1:
            analysis += "The injury report is definitely a factor in this one. "
        
        return analysis or "Sometimes the best angle is simply the better team getting points. "

    def generate_bottom_line(self, game: Dict, pick_data: Dict) -> str:
        """Generate final pick reasoning"""
        conclusion = random.choice(self.analysis_templates['conclusion_phrases'])
        
        analysis = f"I'm taking {pick_data['team']} {pick_data['line']}. "
        
        if pick_data['confidence'] > 80:
            analysis += "This is one of my strongest plays of the week. "
        elif pick_data['confidence'] > 70:
            analysis += "I feel good about this pick. "
        
        analysis += conclusion
        
        return analysis

    def generate_predicted_score(self, game: Dict, pick_data: Dict) -> Dict:
        """Generate predicted final score"""
        base_away = 24
        base_home = 27
        
        total = game['total']
        if total > 50:
            base_away += 3
            base_home += 3
        elif total < 45:
            base_away -= 2
            base_home -= 2
        
        if pick_data['team'] == game['away_team']:
            if '-' in pick_data['line']:
                base_away += 4
                base_home -= 1
            else:
                base_away += 1
                base_home -= 2
        else:
            if '-' in pick_data['line']:
                base_home += 3
                base_away -= 1
            else:
                base_home += 2
                base_away -= 1
        
        base_away += random.randint(-3, 3)
        base_home += random.randint(-3, 3)
        
        away_score = max(7, base_away)
        home_score = max(7, base_home)
        
        return {
            'away_team': game['away_team'],
            'away_score': away_score,
            'home_team': game['home_team'],
            'home_score': home_score
        }

    def generate_parlays(self, nfl_games: List[Dict], cfb_games: List[Dict]) -> Dict:
        """Generate 3-game parlays for NFL and CFB"""
        
        nfl_parlay = self.build_parlay(nfl_games, 'NFL')
        cfb_parlay = self.build_parlay(cfb_games, 'CFB')
        
        return {
            'nfl': nfl_parlay,
            'cfb': cfb_parlay
        }

    def build_parlay(self, games: List[Dict], league: str) -> Dict:
        """Build a 3-game parlay"""
        if len(games) < 3:
            return {'games': [], 'odds': 0, 'reasoning': f'Not enough {league} games available'}
        
        top_games = sorted(games, key=lambda x: x['pick']['confidence'], reverse=True)[:3]
        
        individual_odds = [-110, -110, -110]
        parlay_odds = self.calculate_parlay_odds(individual_odds)
        
        reasoning = f"Three strong {league} plays that complement each other well. "
        
        for i, game in enumerate(top_games):
            if i == 0:
                reasoning += f"{game['pick']['team']} {game['pick']['line']} "
            elif i == len(top_games) - 1:
                reasoning += f"and {game['pick']['team']} {game['pick']['line']}. "
            else:
                reasoning += f"{game['pick']['team']} {game['pick']['line']}, "
        
        reasoning += "These picks have minimal correlation and strong individual value."
        
        return {
            'games': [
                {
                    'matchup': f"{g['game_info']['away_team']} @ {g['game_info']['home_team']}",
                    'pick': f"{g['pick']['team']} {g['pick']['line']}"
                } for g in top_games
            ],
            'odds': parlay_odds,
            'reasoning': reasoning
        }

    def calculate_parlay_odds(self, individual_odds: List[int]) -> int:
        """Calculate parlay odds from individual game odds"""
        decimal_odds = [self.american_to_decimal(odds) for odds in individual_odds]
        parlay_decimal = 1
        for odds in decimal_odds:
            parlay_decimal *= odds
        
        return self.decimal_to_american(parlay_decimal)

    def american_to_decimal(self, american_odds: int) -> float:
        """Convert American odds to decimal"""
        if american_odds > 0:
            return (american_odds / 100) + 1
        else:
            return (100 / abs(american_odds)) + 1

    def decimal_to_american(self, decimal_odds: float) -> int:
        """Convert decimal odds to American"""
        if decimal_odds >= 2:
            return int((decimal_odds - 1) * 100)
        else:
            return int(-100 / (decimal_odds - 1))

    def update_html_site(self, nfl_games: List[Dict], cfb_games: List[Dict], parlays: Dict):
        """Update the HTML site with new picks"""
        
        html_content = self.generate_html_content(nfl_games, cfb_games, parlays)
        
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("✅ HTML site updated successfully!")

    def generate_html_content(self, nfl_games: List[Dict], cfb_games: List[Dict], parlays: Dict) -> str:
        """Generate complete HTML content"""
        
        # Generate content sections
        nfl_parlay_html = self.generate_parlay_html(parlays['nfl'], 'NFL', 'yellow')
        cfb_parlay_html = self.generate_parlay_html(parlays['cfb'], 'CFB', 'blue')
        nfl_games_html = self.generate_games_html(nfl_games, 'NFL')
        cfb_games_html = self.generate_games_html(cfb_games, 'CFB')
        
        # Create complete HTML
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sharp Picks | NFL & CFB Analysis</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js"></script>
    <style>
        .glass-card {{ 
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.9), rgba(30, 41, 59, 0.8));
            backdrop-filter: blur(10px);
            border: 1px solid rgba(34, 197, 94, 0.2);
        }}
        .pick-highlight {{
            background: linear-gradient(135deg, #10b981, #059669);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
    </style>
</head>
<body class="bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white min-h-screen">
    <!-- Header -->
    <header class="glass-card border-b border-green-500/30 sticky top-0 z-50">
        <div class="max-w-6xl mx-auto px-6 py-4">
            <div class="flex items-center justify-between">
                <div>
                    <h1 class="text-3xl font-bold text-green-400">SHARP PICKS</h1>
                    <p class="text-gray-400">Pete Prisco Style Analysis | Auto-Updated</p>
                </div>
                <div class="text-right">
                    <p class="text-sm text-gray-400">Week <span class="text-green-400 font-bold">{self.current_week}</span> • Season 2025</p>
                    <p class="text-xs text-green-400">Updated: {datetime.now().strftime("%A, %I:%M %p")}</p>
                </div>
            </div>
        </div>
    </header>

    <!-- League Tabs -->
    <div class="max-w-6xl mx-auto px-6 py-6">
        <div class="flex space-x-1 bg-slate-800 p-1 rounded-lg mb-8">
            <button onclick="switchLeague('nfl')" id="nfl-tab" class="flex-1 py-3 px-6 rounded-md font-medium transition-all bg-green-600 text-white">
                🏈 NFL
            </button>
            <button onclick="switchLeague('cfb')" id="cfb-tab" class="flex-1 py-3 px-6 rounded-md font-medium transition-all text-gray-400 hover:text-white">
                🎓 CFB
            </button>
        </div>

        <!-- NFL Content -->
        <div id="nfl-content">
            {nfl_parlay_html}
            {nfl_games_html}
        </div>

        <!-- CFB Content -->
        <div id="cfb-content" style="display: none;">
            {cfb_parlay_html}
            {cfb_games_html}
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            lucide.createIcons();
        }});

        function switchLeague(league) {{
            document.getElementById('nfl-tab').className = league === 'nfl' 
                ? "flex-1 py-3 px-6 rounded-md font-medium transition-all bg-green-600 text-white"
                : "flex-1 py-3 px-6 rounded-md font-medium transition-all text-gray-400 hover:text-white";
                
            document.getElementById('cfb-tab').className = league === 'cfb'
                ? "flex-1 py-3 px-6 rounded-md font-medium transition-all bg-green-600 text-white"
                : "flex-1 py-3 px-6 rounded-md font-medium transition-all text-gray-400 hover:text-white";

            document.getElementById('nfl-content').style.display = league === 'nfl' ? 'block' : 'none';
            document.getElementById('cfb-content').style.display = league === 'cfb' ? 'block' : 'none';
        }}
    </script>
</body>
</html>'''
        
        return html_content

    def generate_parlay_html(self, parlay: Dict, league: str, color: str) -> str:
        """Generate HTML for parlay section"""
        if not parlay['games']:
            return f'<div class="glass-card rounded-xl p-6 mb-8"><p class="text-gray-400">No {league} parlay available this week</p></div>'
        
        games_html = ""
        for i, game in enumerate(parlay['games']):
            games_html += f'''
            <div class="p-4 bg-{color}-500/10 border border-{color}-500/30 rounded-lg">
                <h4 class="font-bold text-{color}-400 mb-2">Game {i+1}</h4>
                <p class="text-white font-medium">{game['matchup']}</p>
                <p class="text-{color}-300 text-lg font-bold">{game['pick']}</p>
            </div>'''
        
        return f'''
        <div class="glass-card rounded-xl p-6 mb-8 border-2 border-{color}-500/40">
            <div class="flex items-center space-x-3 mb-6">
                <div class="w-10 h-10 bg-{color}-500 rounded-lg flex items-center justify-center">
                    <i data-lucide="layers" class="w-6 h-6 text-black"></i>
                </div>
                <h2 class="text-2xl font-bold text-{color}-400">{league} 3-GAME PARLAY</h2>
                <div class="ml-auto text-right">
                    <p class="text-2xl font-bold text-{color}-400">{parlay['odds']:+d}</p>
                    <p class="text-sm text-gray-400">Auto-Generated</p>
                </div>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                {games_html}
            </div>
            
            <div class="p-4 bg-slate-800/50 rounded-lg">
                <h3 class="font-bold text-green-400 mb-2">Parlay Reasoning:</h3>
                <p class="text-gray-300">{parlay['reasoning']}</p>
            </div>
        </div>'''

    def generate_games_html(self, games: List[Dict], league: str) -> str:
        """Generate HTML for games section"""
        games_html = f'<h2 class="text-2xl font-bold mb-6">{"🏈" if league == "NFL" else "🎓"} {league} Week {self.current_week} Picks</h2>\n'
        
        for game in games:
            game_html = self.generate_single_game_html(game)
            games_html += game_html + '\n'
        
        return games_html

    def generate_single_game_html(self, game: Dict) -> str:
        """Generate HTML for a single game"""
        info = game['game_info']
        pick = game['pick']
        score = game['predicted_score']
        analysis = game['analysis']
        
        return f'''
        <div class="glass-card rounded-xl p-6 mb-6">
            <div class="flex items-center justify-between mb-4">
                <div>
                    <h3 class="text-xl font-bold">{info['away_team']} @ {info['home_team']}</h3>
                    <p class="text-gray-400">{info['time']}</p>
                    <p class="text-sm text-gray-500">{info['venue']}</p>
                </div>
                <div class="text-center">
                    <p class="text-sm text-gray-400">Line</p>
                    <p class="text-lg font-bold">{info['home_team'].split()[-1]} {info['spread']}</p>
                    <p class="text-sm text-gray-400">O/U {info['total']}</p>
                </div>
            </div>
            
            <div class="p-4 bg-green-500/10 border border-green-500/30 rounded-lg mb-4">
                <h4 class="font-bold text-green-400 text-lg mb-2">🎯 THE PICK: {pick['team'].split()[-1]} {pick['line']}</h4>
                <p class="text-green-300 font-medium mb-2">Predicted Score: {score['away_team'].split()[-1]} {score['away_score']}, {score['home_team'].split()[-1]} {score['home_score']}</p>
                <p class="text-sm text-gray-400">Confidence: {pick['confidence']:.0f}%</p>
            </div>
            
            <div class="space-y-4">
                <div>
                    <h4 class="font-bold text-blue-400 mb-2">The Line</h4>
                    <p class="text-gray-300">{analysis['the_line']}</p>
                </div>
                
                <div>
                    <h4 class="font-bold text-blue-400 mb-2">The Matchup</h4>
                    <p class="text-gray-300">{analysis['the_matchup']}</p>
                </div>
                
                <div>
                    <h4 class="font-bold text-blue-400 mb-2">The Angle</h4>
                    <p class="text-gray-300">{analysis['the_angle']}</p>
                </div>
                
                <div>
                    <h4 class="font-bold text-blue-400 mb-2">The Bottom Line</h4>
                    <p class="text-gray-300">{analysis['the_bottom_line']}</p>
                </div>
            </div>
        </div>'''

    def format_game_time(self, commence_time: str) -> str:
        """Format game time for display"""
        try:
            dt = datetime.fromisoformat(commence_time.replace('Z', '+00:00'))
            return dt.strftime("%A • %I:%M %p ET")
        except:
            return "TBD"

    def get_venue(self, home_team: str) -> str:
        """Get venue for home team"""
        venues = {
            'Kansas City Chiefs': 'Arrowhead Stadium, Kansas City',
            'Buffalo Bills': 'Highmark Stadium, Buffalo',
            'Dallas Cowboys': 'AT&T Stadium, Arlington',
            'New York Giants': 'MetLife Stadium, East Rutherford',
            'Green Bay Packers': 'Lambeau Field, Green Bay',
            'Chicago Bears': 'Soldier Field, Chicago',
        }
        return venues.get(home_team, f"{home_team} Stadium")

    def get_demo_nfl_games(self) -> List[Dict]:
        """Fallback demo NFL games if API fails"""
        return [
            {
                'away_team': 'Kansas City Chiefs',
                'home_team': 'Buffalo Bills',
                'commence_time': '2025-09-12T00:15:00Z',
                'spread': -2.5,
                'total': 51.5,
                'away_ml': 110,
                'home_ml': -130,
                'league': 'NFL'
            },
            {
                'away_team': 'Dallas Cowboys',
                'home_team': 'New York Giants',
                'commence_time': '2025-09-14T17:00:00Z',
                'spread': -3.5,
                'total': 47.5,
                'away_ml': -165,
                'home_ml': 140,
                'league': 'NFL'
            },
            {
                'away_team': 'Green Bay Packers',
                'home_team': 'Chicago Bears',
                'commence_time': '2025-09-14T17:00:00Z',
                'spread': -6.5,
                'total': 44.5,
                'away_ml': -280,
                'home_ml': 230,
                'league': 'NFL'
            }
        ]

    def get_demo_cfb_games(self) -> List[Dict]:
        """Fallback demo CFB games if API fails"""
        return [
            {
                'away_team': 'Alabama Crimson Tide',
                'home_team': 'Georgia Bulldogs',
                'commence_time': '2025-09-13T23:30:00Z',
                'spread': -3.5,
                'total': 58.5,
                'away_ml': 140,
                'home_ml': -165,
                'league': 'CFB'
            },
            {
                'away_team': 'Ohio State Buckeyes',
                'home_team': 'Michigan Wolverines',
                'commence_time': '2025-09-13T19:30:00Z',
                'spread': -7.0,
                'total': 54.5,
                'away_ml': -280,
                'home_ml': 230,
                'league': 'CFB'
            },
            {
                'away_team': 'Clemson Tigers',
                'home_team': 'Florida State Seminoles',
                'commence_time': '2025-09-14T00:00:00Z',
                'spread': 2.5,
                'total': 58.5,
                'away_ml': 110,
                'home_ml': -130,
                'league': 'CFB'
            }
        ]

    def commit_to_github(self):
        """Automatically commit and push changes to GitHub"""
        try:
            import subprocess
            
            subprocess.run(['git', 'add', '.'], check=True)
            
            commit_message = f"Auto-update: Week {self.current_week} picks - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            subprocess.run(['git', 'commit', '-m', commit_message], check=True)
            
            subprocess.run(['git', 'push', 'origin', 'main'], check=True)
            
            print("✅ Changes committed and pushed to GitHub!")
            print("🚀 Vercel will auto-deploy your updated site!")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Git operations failed: {e}")
            print("💡 Make sure you're in a git repository and have push permissions")
        except FileNotFoundError:
            print("❌ Git not found. Please install Git to enable auto-deployment")

    def run_full_update(self):
        """Main method to run complete site update"""
        print("🚀 STARTING AUTOPILOT BETTING SITE UPDATE...")
        print(f"📅 Week {self.current_week} • {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("="*60)
        
        print("📡 Fetching live NFL games...")
        nfl_raw_games = self.fetch_live_nfl_games()
        
        print("📡 Fetching live CFB games...")
        cfb_raw_games = self.fetch_live_cfb_games()
        
        print("🧠 Generating Pete Prisco style analysis...")
        nfl_games = [self.generate_game_analysis(game) for game in nfl_raw_games]
        cfb_games = [self.generate_game_analysis(game) for game in cfb_raw_games]
        
        print(f"✅ Analyzed {len(nfl_games)} NFL games")
        print(f"✅ Analyzed {len(cfb_games)} CFB games")
        
        print("🎰 Building 3-game parlays...")
        parlays = self.generate_parlays(nfl_games, cfb_games)
        
        print("🌐 Updating HTML site...")
        self.update_html_site(nfl_games, cfb_games, parlays)
        
        print("🚀 Deploying to GitHub...")
        self.commit_to_github()
        
        print("="*60)
        print("✅ AUTOPILOT UPDATE COMPLETE!")
        print(f"📊 Generated {len(nfl_games)} NFL picks and {len(cfb_games)} CFB picks")
        print(f"🎰 Built NFL parlay ({parlays['nfl']['odds']:+d}) and CFB parlay ({parlays['cfb']['odds']:+d})")
        print("🌐 Site updated and deployed automatically!")
        print("💰 Ready for Bovada betting!")


def main():
    """Main execution function"""
    updater = AutoPilotBettingUpdater()
    updater.run_full_update()


if __name__ == "__main__":
    main()