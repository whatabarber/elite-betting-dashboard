def generate_line_analysis(self, game: Dict, pick_data: Dict) -> str:
        """Generate analysis of the betting line"""
        hook = random.choice(self.analysis_templates['opening_hooks'])
        
        spread = abs(game['spread'])
        public_side = "favorite" if pick_data['factors']['public_betting'] > 0.6 else "underdog"
        
        analysis = f"{hook} "
        
        if spread <= 3:
            analysis += f"This is essentially a pick'em game, but the {spread}-point spread tells a story. "
        elif spread <= 7:
            analysis += f"The {spread}-point spread feels about right on paper, but the advanced metrics suggest otherwise. "
        else:
            analysis += f"That's a big number at {spread} points. The rankings and stats justify this line. "
        
        if pick_data['factors']['public_betting'] > 0.7:
            analysis += f"The public is hammering the {public_side}, which is exactly why I'm fading them. "
        
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
        
        # Add ranking-based analysis
        if abs(pick_data['factors']['ranking_edge']) > 1:
            analysis += "The advanced metrics and rankings strongly favor one side here. "
        
        return analysis or "Sometimes the best angle is simply the better team getting points. "

    def generate_bottom_line(self, game: Dict, pick_data: Dict) -> str:
        """Generate final pick reasoning with units"""
        conclusion = random.choice(self.analysis_templates['conclusion_phrases'])
        
        analysis = f"I'm taking {pick_data['team']} {pick_data['line']} ({pick_data['units']}). "
        
        if pick_data['confidence'] > 85:
            analysis += "This is one of my strongest plays of the week. "
        elif pick_data['confidence'] > 75:
            analysis += "I feel very good about this pick. "
        elif pick_data['confidence'] > 65:
            analysis += "Solid value play here. "
        
        analysis += conclusion
        
        return analysis

    def generate_predicted_score(self, game: Dict, pick_data: Dict) -> Dict:
        """Generate predicted final score"""
        # Start with team averages if available
        base_away = 24
        base_home = 27
        
        total = game['total']
        if total > 50:
            base_away += 2
            base_home += 2
        elif total < 45:
            base_away -= 2
            base_home -= 2
        
        # Adjust based on pick
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
        
        away_score = max(7, int(base_away))
        home_score = max(7, int(base_home))
        
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
        
        reasoning = f"Three elite {league} plays with strong analytical backing. "
        
        for i, game in enumerate(top_games):
            if i == 0:
                reasoning += f"{game['pick']['team'].split()[-1]} {game['pick']['line']} ({game['pick']['units']}) "
            elif i == len(top_games) - 1:
                reasoning += f"and {game['pick']['team'].split()[-1]} {game['pick']['line']} ({game['pick']['units']}). "
            else:
                reasoning += f"{game['pick']['team'].split()[-1]} {game['pick']['line']} ({game['pick']['units']}), "
        
        reasoning += "The advanced metrics support all three picks with minimal correlation risk."
        
        return {
            'games': [
                {
                    'matchup': f"{g['game_info']['away_team']} @ {g['game_info']['home_team']}",
                    'pick': f"{g['pick']['team'].split()[-1]} {g['pick']['line']} ({g['pick']['units']})",
                    'confidence': g['pick']['confidence']
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

    def update_html_site(self, nfl_games: List[Dict], cfb_games: List[Dict], parlays: Dict, nfl_props: List[Dict] = None, cfb_props: List[Dict] = None):
        """Update the HTML site with new picks and props"""
        
        html_content = self.generate_elite_html_content(nfl_games, cfb_games, parlays, nfl_props or [], cfb_props or [])
        
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("✅ Elite HTML site updated successfully!")

    def generate_elite_html_content(self, nfl_games: List[Dict], cfb_games: List[Dict], parlays: Dict, nfl_props: List[Dict], cfb_props: List[Dict]) -> str:
        """Generate complete elite HTML content with props and rankings"""
        
        # Generate content sections
        nfl_parlay_html = self.generate_elite_parlay_html(parlays['nfl'], 'NFL', 'yellow')
        cfb_parlay_html = self.generate_elite_parlay_html(parlays['cfb'], 'CFB', 'blue')
        nfl_games_html = self.generate_elite_games_html(nfl_games, 'NFL')
        cfb_games_html = self.generate_elite_games_html(cfb_games, 'CFB')
        nfl_props_html = self.generate_props_html(nfl_props, 'NFL')
        cfb_props_html = self.generate_props_html(cfb_props, 'CFB')
        
        # Create complete HTML
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Elite Sharp Picks | NFL & CFB Analysis v2.0</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js"></script>
    <style>
        .glass-card {{ 
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.85));
            backdrop-filter: blur(12px);
            border: 1px solid rgba(34, 197, 94, 0.3);
        }}
        .elite-gradient {{
            background: linear-gradient(135deg, #10b981, #059669, #047857);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .ranking-badge {{
            background: linear-gradient(135deg, #fbbf24, #f59e0b);
            border-radius: 6px;
            padding: 2px 8px;
            font-size: 0.75rem;
            font-weight: bold;
            color: #000;
        }}
        .units-badge {{
            background: linear-gradient(135deg, #ef4444, #dc2626);
            border-radius: 4px;
            padding: 2px 6px;
            font-size: 0.7rem;
            font-weight: bold;
            color: white;
        }}
    </style>
</head>
<body class="bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white min-h-screen">
    <header class="glass-card border-b border-green-500/40 sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-6 py-4">
            <div class="flex items-center justify-between">
                <div>
                    <h1 class="text-4xl font-bold elite-gradient">WHATABARBER'S ELITE PICKS</h1>
                    <p class="text-gray-400">🔥 Advanced Analytics • Player Props • Live Discord Alerts</p>
                </div>
                <div class="text-right">
                    <p class="text-sm text-gray-400">Week <span class="text-green-400 font-bold">{self.current_week}</span> • Season 2025</p>
                    <p class="text-xs text-green-400">Last Updated: {datetime.now().strftime("%A, %I:%M %p")}</p>
                    <p class="text-xs text-yellow-400">⚡ Auto-Discord Alerts Active</p>
                </div>
            </div>
        </div>
    </header>

    <div class="max-w-7xl mx-auto px-6 py-6">
        <div class="flex space-x-1 bg-slate-800 p-1 rounded-lg mb-8">
            <button onclick="switchLeague('nfl')" id="nfl-tab" class="flex-1 py-3 px-6 rounded-md font-medium transition-all bg-green-600 text-white">
                🏈 NFL
            </button>
            <button onclick="switchLeague('cfb')" id="cfb-tab" class="flex-1 py-3 px-6 rounded-md font-medium transition-all text-gray-400 hover:text-white">
                🎓 CFB
            </button>
        </div>

        <div id="nfl-content">
            {nfl_parlay_html}
            {nfl_props_html}
            {nfl_games_html}
        </div>

        <div id="cfb-content" style="display: none;">
            {cfb_parlay_html}
            {cfb_props_html}
            {cfb_games_html}
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            lucide.createIcons();
        }});

        function switchLeague(league) {{
            const nflTab = document.getElementById('nfl-tab');
            const cfbTab = document.getElementById('cfb-tab');
            const nflContent = document.getElementById('nfl-content');
            const cfbContent = document.getElementById('cfb-content');
            
            if (league === 'nfl') {{
                nflTab.className = "flex-1 py-3 px-6 rounded-md font-medium transition-all bg-green-600 text-white";
                cfbTab.className = "flex-1 py-3 px-6 rounded-md font-medium transition-all text-gray-400 hover:text-white";
                nflContent.style.display = 'block';
                cfbContent.style.display = 'none';
            }} else {{
                nflTab.className = "flex-1 py-3 px-6 rounded-md font-medium transition-all text-gray-400 hover:text-white";
                cfbTab.className = "flex-1 py-3 px-6 rounded-md font-medium transition-all bg-green-600 text-white";
                nflContent.style.display = 'none';
                cfbContent.style.display = 'block';
            }}
        }}
    </script>
</body>
</html>"""
        
        return html_content

    def generate_elite_parlay_html(self, parlay: Dict, league: str, color: str) -> str:
        """Generate HTML for elite parlay section with confidence scores"""
        if not parlay['games']:
            return f'<div class="glass-card rounded-xl p-6 mb-8"><p class="text-gray-400">No {league} parlay available this week</p></div>'
        
        games_html = ""
        for i, game in enumerate(parlay['games']):
            confidence = game.get('confidence', 75)
            conf_color = 'green' if confidence >= 80 else 'yellow' if confidence >= 70 else 'orange'
            
            games_html += f"""
            <div class="p-4 bg-{color}-500/10 border border-{color}-500/30 rounded-lg">
                <div class="flex justify-between items-start mb-2">
                    <h4 class="font-bold text-{color}-400">Game {i+1}</h4>
                    <span class="text-{conf_color}-400 text-sm font-bold">{confidence:.0f}% Confidence</span>
                </div>
                <p class="text-white font-medium">{game['matchup']}</p>
                <p class="text-{color}-300 text-lg font-bold">{game['pick']}</p>
            </div>"""
        
        return f"""
        <div class="glass-card rounded-xl p-6 mb-8 border-2 border-{color}-500/50">
            <div class="flex items-center space-x-3 mb-6">
                <div class="w-12 h-12 bg-{color}-500 rounded-lg flex items-center justify-center">
                    <i data-lucide="layers" class="w-7 h-7 text-black"></i>
                </div>
                <h2 class="text-3xl font-bold text-{color}-400">{league} ELITE 3-GAME PARLAY</h2>
                <div class="ml-auto text-right">
                    <p class="text-3xl font-bold text-{color}-400">{parlay['odds']:+d}</p>
                    <p class="text-sm text-gray-400">Algorithm Generated</p>
                </div>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                {games_html}
            </div>
            
            <div class="p-4 bg-slate-800/60 rounded-lg border border-green-500/20">
                <h3 class="font-bold text-green-400 mb-2">🧠 Elite Analysis:</h3>
                <p class="text-gray-300">{parlay['reasoning']}</p>
            </div>
        </div>"""

    def generate_props_html(self, props: List[Dict], league: str) -> str:
        """Generate HTML for player props section"""
        if not props:
            return ""
        
        props_html = f"""
        <div class="glass-card rounded-xl p-6 mb-8">
            <div class="flex items-center space-x-3 mb-6">
                <div class="w-10 h-10 bg-purple-500 rounded-lg flex items-center justify-center">
                    <i data-lucide="target" class="w-6 h-6 text-white"></i>
                </div>
                <h2 class="text-2xl font-bold text-purple-400">🎯 {league} ELITE PLAYER PROPS</h2>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">"""
        
        for prop in props:
            conf_color = 'green' if prop['confidence'] >= 80 else 'yellow' if prop['confidence'] >= 70 else 'orange'
            
            props_html += f"""
                <div class="p-4 bg-purple-500/10 border border-purple-500/30 rounded-lg">
                    <div class="flex justify-between items-start mb-2">
                        <h4 class="font-bold text-purple-300 text-sm">{prop['prop']['market'].replace('_', ' ').title()}</h4>
                        <span class="text-{conf_color}-400 text-xs font-bold">{prop['confidence']:.0f}%</span>
                    </div>
                    <p class="text-white font-medium text-sm mb-1">{prop['prop']['player']}</p>
                    <p class="text-purple-400 font-bold">{prop['pick']}</p>
                    <p class="text-gray-400 text-xs mt-2">{prop['reasoning']}</p>
                </div>"""
        
        props_html += """
            </div>
        </div>"""
        
        return props_html

    def generate_elite_games_html(self, games: List[Dict], league: str) -> str:
        """Generate HTML for games section with rankings and advanced stats"""
        games_html = f'<h2 class="text-2xl font-bold mb-6">{"🏈" if league == "NFL" else "🎓"} {league} Week {self.current_week} Elite Analysis</h2>'
        
        for game in games:
            info = game['game_info']
            pick = game['pick']
            score = game['predicted_score']
            analysis = game['analysis']
            away_stats = info['away_stats']
            home_stats = info['home_stats']
            
            # Confidence color coding
            conf_color = 'green' if pick['confidence'] >= 80 else 'yellow' if pick['confidence'] >= 70 else 'orange'
            
            games_html += f"""
            <div class="glass-card rounded-xl p-6 mb-6">
                <div class="flex items-center justify-between mb-4">
                    <div>
                        <h3 class="text-xl font-bold">{info['away_team']} ({info['away_record']}) @ {info['home_team']} ({info['home_record']})</h3>
                        <p class="text-gray-400">{info['time']}</p>
                        <p class="text-sm text-gray-500">{info['venue']}</p>
                    </div>
                    <div class="text-center">
                        <p class="text-sm text-gray-400">Line</p>
                        <p class="text-lg font-bold">{info['home_team'].split()[-1]} {info['spread']}</p>
                        <p class="text-sm text-gray-400">O/U {info['total']}</p>
                    </div>
                </div>
                
                <!-- Team Rankings Section -->
                <div class="grid grid-cols-2 gap-4 mb-4 p-4 bg-slate-800/30 rounded-lg">
                    <div class="text-center">
                        <h4 class="font-bold text-blue-400 mb-2">{info['away_team'].split()[-1]} Rankings</h4>
                        <div class="grid grid-cols-2 gap-2 text-xs">
                            <div><span class="ranking-badge">#{away_stats['offense_rank']}</span> Offense</div>
                            <div><span class="ranking-badge">#{away_stats['defense_rank']}</span> Defense</div>
                            <div><span class="ranking-badge">#{away_stats['rush_offense']}</span> Rush O</div>
                            <div><span class="ranking-badge">#{away_stats['rush_defense']}</span> Rush D</div>
                            <div><span class="ranking-badge">#{away_stats['pass_offense']}</span> Pass O</div>
                            <div><span class="ranking-badge">#{away_stats['pass_defense']}</span> Pass D</div>
                        </div>
                        <p class="text-xs text-gray-400 mt-1">{away_stats['points_for']:.1f} PPG • {away_stats['points_against']:.1f} Allowed</p>
                    </div>
                    <div class="text-center">
                        <h4 class="font-bold text-red-400 mb-2">{info['home_team'].split()[-1]} Rankings</h4>
                        <div class="grid grid-cols-2 gap-2 text-xs">
                            <div><span class="ranking-badge">#{home_stats['offense_rank']}</span> Offense</div>
                            <div><span class="ranking-badge">#{home_stats['defense_rank']}</span> Defense</div>
                            <div><span class="ranking-badge">#{home_stats['rush_offense']}</span> Rush O</div>
                            <div><span class="ranking-badge">#{home_stats['rush_defense']}</span> Rush D</div>
                            <div><span class="ranking-badge">#{home_stats['pass_offense']}</span> Pass O</div>
                            <div><span class="ranking-badge">#{home_stats['pass_defense']}</span> Pass D</div>
                        </div>
                        <p class="text-xs text-gray-400 mt-1">{home_stats['points_for']:.1f} PPG • {home_stats['points_against']:.1f} Allowed</p>
                    </div>
                </div>
                
                <div class="p-4 bg-green-500/10 border border-green-500/30 rounded-lg mb-4">
                    <div class="flex items-center justify-between mb-2">
                        <h4 class="font-bold text-green-400 text-lg">🎯 ELITE PICK: {pick['team'].split()[-1]} {pick['line']}</h4>
                        <div class="flex space-x-2">
                            <span class="units-badge">{pick['units']}</span>
                            <span class="text-{conf_color}-400 font-bold">{pick['confidence']:.0f}%</span>
                        </div>
                    </div>
                    <p class="text-green-300 font-medium mb-2">Predicted Score: {score['away_team'].split()[-1]} {score['away_score']}, {score['home_team'].split()[-1]} {score['home_score']}</p>
                </div>
                
                <div class="space-y-4">
                    <div>
                        <h4 class="font-bold text-blue-400 mb-2">📊 The Line</h4>
                        <p class="text-gray-300">{analysis['the_line']}</p>
                    </div>
                    
                    <div>
                        <h4 class="font-bold text-blue-400 mb-2">⚔️ Advanced Matchup Analysis</h4>
                        <p class="text-gray-300">{analysis['the_matchup']}</p>
                    </div>
                    
                    <div>
                        <h4 class="font-bold text-blue-400 mb-2">🎯 The Sharp Angle</h4>
                        <p class="text-gray-300">{analysis['the_angle']}</p>
                    </div>
                    
                    <div>
                        <h4 class="font-bold text-blue-400 mb-2">💰 The Bottom Line</h4>
                        <p class="text-gray-300">{analysis['the_bottom_line']}</p>
                    </div>
                </div>
            </div>"""
        
        return games_html

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
            'Alabama Crimson Tide': 'Bryant-Denny Stadium, Tuscaloosa',
            'Georgia Bulldogs': 'Sanford Stadium, Athens',
            'Ohio State Buckeyes': 'Ohio Stadium, Columbus',
            'Michigan Wolverines': 'Michigan Stadium, Ann Arbor',
            'Clemson Tigers': 'Memorial Stadium, Clemson',
            'Florida State Seminoles': 'Doak Campbell Stadium, Tallahassee'
        }
        return venues.get(home_team, f"{home_team} Stadium")

    def commit_to_github(self):
        """Automatically commit and push changes to GitHub"""
        try:
            import subprocess
            
            subprocess.run(['git', 'add', '.'], check=True)
            
            commit_message = f"Elite Auto-update: Week {self.current_week} picks with props & rankings - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            subprocess.run(['git', 'commit', '-m', commit_message], check=True)
            
            subprocess.run(['git', 'push', 'origin', 'main'], check=True)
            
            print("✅ Elite changes committed and pushed to GitHub!")
            print("🚀 Vercel will auto-deploy your updated elite site!")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Git operations failed: {e}")
            print("💡 Make sure you're in a git repository and have push permissions")
        except FileNotFoundError:
            print("❌ Git not found. Please install Git to enable auto-deployment")

    async def run_full_elite_update(self):
        """Main method to run complete elite site update with Discord alerts"""
        print("🔥 STARTING ELITE AUTOPILOT BETTING SITE UPDATE v2.0...")
        print(f"📅 Week {self.current_week} • {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("⚡ Discord alerts enabled • Player props analysis • Advanced rankings")
        print("="*70)
        
        print("📡 Fetching live NFL games...")
        nfl_raw_games = self.fetch_live_nfl_games()
        
        print("📡 Fetching live CFB games...")
        cfb_raw_games = self.fetch_live_cfb_games()
        
        print("🎯 Fetching NFL player props...")
        nfl_props_raw = self.fetch_player_props('NFL')
        
        print("🎯 Fetching CFB player props...")
        cfb_props_raw = self.fetch_player_props('CFB')
        
        print("🧠 Generating elite Pete Prisco style analysis...")
        nfl_games = [self.generate_game_analysis(game) for game in nfl_raw_games]
        cfb_games = [self.generate_game_analysis(game) for game in cfb_raw_games]
        
        print("🎯 Analyzing player props for value...")
        nfl_props = self.analyze_player_props(nfl_props_raw, 'NFL')
        cfb_props = self.analyze_player_props(cfb_props_raw, 'CFB')
        
        print(f"✅ Analyzed {len(nfl_games)} NFL games with rankings")
        print(f"✅ Analyzed {len(cfb_games)} CFB games with rankings")
        print(f"🎯 Found {len(nfl_props)} elite NFL props")
        print(f"🎯 Found {len(cfb_props)} elite CFB props")
        
        print("🎰 Building elite 3-game parlays...")
        parlays = self.generate_parlays(nfl_games, cfb_games)
        
        print("🌐 Updating elite HTML site...")
        self.update_html_site(nfl_games, cfb_games, parlays, nfl_props, cfb_props)
        
        print("🔥 Preparing Discord alerts...")
        high_confidence_picks = [game for game in nfl_games + cfb_games if game['pick']['confidence'] >= 75]
        high_confidence_picks.sort(key=lambda x: x['pick']['confidence'], reverse=True)
        
        print("📱 Sending Discord webhook alerts...")
        await self.send_discord_alert(parlays, high_confidence_picks)
        
        print("🚀 Deploying to GitHub...")
        self.commit_to_github()
        
        print("="*70)
        print("🔥 ELITE AUTOPILOT UPDATE COMPLETE! 🔥")
        print(f"📊 Generated {len(nfl_games)} NFL + {len(cfb_games)} CFB elite picks")
        print(f"🎯 Found {len(nfl_props + cfb_props)} sharp player props")
        print(f"🎰 Built NFL parlay ({parlays['nfl']['odds']:+d}) and CFB parlay ({parlays['cfb']['odds']:+d})")
        print(f"⚡ Sent Discord alerts for {len(high_confidence_picks)} high confidence picks")
        print("🌐 Elite site updated with rankings, props, and units!")
        print("💰 Ready for Bovada betting with maximum edge!")
        
        # Print summary for user
        print("\n🎯 ELITE PICKS SUMMARY:")
        print("-" * 50)
        for game in high_confidence_picks[:5]:
            conf = game['pick']['confidence']
            units = game['pick']['units']
            print(f"• {game['pick']['team'].split()[-1]} {game['pick']['line']} ({units}) - {conf:.0f}% confidence")


def main():
    """Main execution function"""
    import asyncio
    
    async def run_updater():
        updater = EliteAutoPilotBettingUpdater()
        await updater.run_full_elite_update()
    
    # Run the async function
    asyncio.run(run_updater())


if __name__ == "__main__":
    main()#!/usr/bin/env python3
"""
ELITE AUTOPILOT BETTING SITE UPDATER v2.0
🔥 Now with Discord alerts, player props, team rankings, and records!
Run weekly to get sharp-level analysis and auto-alerts
"""

import requests
import json
import random
from datetime import datetime, timedelta
import os
from typing import List, Dict, Any
import asyncio
import aiohttp

class EliteAutoPilotBettingUpdater:
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
        
        # Discord webhook URL
        self.discord_webhook = "https://discord.com/api/webhooks/1403458907929710634/JC8tYkcyAIoQVLKssIhhGTWRTG1zAzzppkRjRvAN7C2FTGRSS-k52C8Yhuw1W2N5DZiA"
        
        self.current_week = self.get_current_week()
        self.bovada_focus = True
        
        # Team records and rankings database (will be dynamic in real season)
        self.team_data = self.initialize_team_data()
        
        # Analysis templates
        self.analysis_templates = {
            'opening_hooks': [
                "This line screams trap game to me.",
                "The books are begging you to take the obvious side here.",
                "Classic case of the public being wrong.",
                "This is the type of spot that separates the pros from the squares.",
                "The sharps have been all over this number.",
                "Public money is flowing one way, but I'm going the other.",
                "The advanced metrics tell a different story here.",
                "This is exactly the type of spot sharp money loves.",
            ],
            'matchup_intros': [
                "Let's break down what really matters in this matchup.",
                "The key to this game comes down to a few critical factors.",
                "When you dig into the numbers, the story becomes clear.",
                "This matchup has several interesting angles.",
                "The tape tells a different story than the line suggests.",
                "The advanced stats reveal the real edge here.",
            ],
            'conclusion_phrases': [
                "Take the points and run.",
                "This one won't be close.",
                "I'm confident in this pick.",
                "The value is too good to pass up.",
                "This is a max play for me.",
                "Lock it in and don't look back.",
                "Sharp money is all over this.",
                "The metrics don't lie on this one.",
            ]
        }

    def initialize_team_data(self) -> Dict:
        """Initialize team records and rankings - will be dynamic in real season"""
        return {
            'nfl': {
                'Kansas City Chiefs': {
                    'record': '8-2',
                    'offense_rank': 3,
                    'defense_rank': 12,
                    'rush_offense': 18,
                    'rush_defense': 8,
                    'pass_offense': 2,
                    'pass_defense': 15,
                    'points_for': 28.4,
                    'points_against': 19.8
                },
                'Buffalo Bills': {
                    'record': '7-3',
                    'offense_rank': 5,
                    'defense_rank': 9,
                    'rush_offense': 22,
                    'rush_defense': 6,
                    'pass_offense': 4,
                    'pass_defense': 11,
                    'points_for': 26.8,
                    'points_against': 20.1
                },
                'Dallas Cowboys': {
                    'record': '6-4',
                    'offense_rank': 8,
                    'defense_rank': 14,
                    'rush_offense': 16,
                    'rush_defense': 18,
                    'pass_offense': 6,
                    'pass_defense': 12,
                    'points_for': 24.9,
                    'points_against': 22.3
                },
                'New York Giants': {
                    'record': '4-6',
                    'offense_rank': 24,
                    'defense_rank': 16,
                    'rush_offense': 28,
                    'rush_defense': 11,
                    'pass_offense': 19,
                    'pass_defense': 20,
                    'points_for': 19.8,
                    'points_against': 23.7
                },
                'Green Bay Packers': {
                    'record': '7-3',
                    'offense_rank': 4,
                    'defense_rank': 7,
                    'rush_offense': 12,
                    'rush_defense': 4,
                    'pass_offense': 3,
                    'pass_defense': 9,
                    'points_for': 27.2,
                    'points_against': 18.9
                },
                'Chicago Bears': {
                    'record': '3-7',
                    'offense_rank': 26,
                    'defense_rank': 13,
                    'rush_offense': 24,
                    'rush_defense': 10,
                    'pass_offense': 28,
                    'pass_defense': 16,
                    'points_for': 18.4,
                    'points_against': 24.1
                }
            },
            'cfb': {
                'Alabama Crimson Tide': {
                    'record': '9-1',
                    'offense_rank': 2,
                    'defense_rank': 8,
                    'rush_offense': 15,
                    'rush_defense': 5,
                    'pass_offense': 1,
                    'pass_defense': 12,
                    'points_for': 42.8,
                    'points_against': 18.2
                },
                'Georgia Bulldogs': {
                    'record': '8-2',
                    'offense_rank': 6,
                    'defense_rank': 3,
                    'rush_offense': 8,
                    'rush_defense': 2,
                    'pass_offense': 11,
                    'pass_defense': 4,
                    'points_for': 35.4,
                    'points_against': 14.7
                },
                'Ohio State Buckeyes': {
                    'record': '9-1',
                    'offense_rank': 3,
                    'defense_rank': 6,
                    'rush_offense': 12,
                    'rush_defense': 8,
                    'pass_offense': 2,
                    'pass_defense': 7,
                    'points_for': 41.2,
                    'points_against': 16.9
                },
                'Michigan Wolverines': {
                    'record': '7-3',
                    'offense_rank': 18,
                    'defense_rank': 4,
                    'rush_offense': 6,
                    'rush_defense': 3,
                    'pass_offense': 24,
                    'pass_defense': 5,
                    'points_for': 28.7,
                    'points_against': 17.8
                },
                'Clemson Tigers': {
                    'record': '8-2',
                    'offense_rank': 12,
                    'defense_rank': 11,
                    'rush_offense': 18,
                    'rush_defense': 14,
                    'pass_offense': 8,
                    'pass_defense': 9,
                    'points_for': 32.1,
                    'points_against': 19.4
                },
                'Florida State Seminoles': {
                    'record': '6-4',
                    'offense_rank': 22,
                    'defense_rank': 15,
                    'rush_offense': 26,
                    'rush_defense': 18,
                    'pass_offense': 16,
                    'pass_defense': 13,
                    'points_for': 26.8,
                    'points_against': 23.1
                }
            }
        }

    def get_current_week(self) -> int:
        """Calculate current NFL week"""
        season_start = datetime(2025, 9, 5)  # Adjusted for 2025 season
        now = datetime.now()
        weeks_passed = (now - season_start).days // 7
        return max(1, min(weeks_passed + 1, 18))

    async def send_discord_alert(self, parlays: Dict, high_confidence_picks: List[Dict]):
        """Send Discord webhook alerts for high confidence parlays and picks"""
        try:
            embed_data = self.create_discord_embed(parlays, high_confidence_picks)
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.discord_webhook, json=embed_data) as response:
                    if response.status == 204:
                        print("✅ Discord alert sent successfully!")
                    else:
                        print(f"❌ Discord alert failed: {response.status}")
                        
        except Exception as e:
            print(f"❌ Discord alert error: {e}")

    def create_discord_embed(self, parlays: Dict, high_confidence_picks: List[Dict]) -> Dict:
        """Create Discord embed for alerts"""
        
        # Create NFL parlay field
        nfl_parlay_value = ""
        if parlays['nfl']['games']:
            for i, game in enumerate(parlays['nfl']['games']):
                nfl_parlay_value += f"**{i+1}.** {game['pick']}\n"
            nfl_parlay_value += f"**Odds:** {parlays['nfl']['odds']:+d}"
        else:
            nfl_parlay_value = "No NFL parlay this week"
        
        # Create CFB parlay field
        cfb_parlay_value = ""
        if parlays['cfb']['games']:
            for i, game in enumerate(parlays['cfb']['games']):
                cfb_parlay_value += f"**{i+1}.** {game['pick']}\n"
            cfb_parlay_value += f"**Odds:** {parlays['cfb']['odds']:+d}"
        else:
            cfb_parlay_value = "No CFB parlay this week"
        
        # High confidence picks
        high_conf_value = ""
        for pick in high_confidence_picks[:5]:  # Top 5 only
            conf = pick['pick']['confidence']
            high_conf_value += f"**{pick['game_info']['away_team']} @ {pick['game_info']['home_team']}**\n"
            high_conf_value += f"Pick: {pick['pick']['team'].split()[-1]} {pick['pick']['line']} ({conf:.0f}%)\n\n"
        
        if not high_conf_value:
            high_conf_value = "No high confidence picks this week"
        
        embed_data = {
            "embeds": [
                {
                    "title": "🔥 WHATABARBER'S ELITE PICKS ALERT 🔥",
                    "description": f"**Week {self.current_week} • Auto-Generated Sharp Picks**\n\n*The algorithm has found value...*",
                    "color": 0x00ff41,  # Green color
                    "timestamp": datetime.now().isoformat(),
                    "fields": [
                        {
                            "name": "🏈 NFL 3-GAME PARLAY",
                            "value": nfl_parlay_value,
                            "inline": False
                        },
                        {
                            "name": "🎓 CFB 3-GAME PARLAY", 
                            "value": cfb_parlay_value,
                            "inline": False
                        },
                        {
                            "name": "⚡ HIGH CONFIDENCE SINGLES",
                            "value": high_conf_value,
                            "inline": False
                        }
                    ],
                    "footer": {
                        "text": "💰 Auto-Updated • Ready for Bovada",
                        "icon_url": "https://cdn.discordapp.com/attachments/123456789/money_emoji.png"
                    },
                    "thumbnail": {
                        "url": "https://cdn.discordapp.com/attachments/123456789/football_emoji.png"
                    }
                }
            ]
        }
        
        return embed_data

    def fetch_live_nfl_games(self) -> List[Dict]:
        """Fetch live NFL games and odds - NO DEMO FALLBACK"""
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
            
            print(f"✅ Fetched {len(processed_games)} REAL NFL games from API")
            return processed_games
            
        except Exception as e:
            print(f"❌ Failed to fetch NFL games: {e}")
            print("💡 Check your ODDS_API_KEY in .env file")
            return []  # Return empty list, NO DEMO

    def fetch_live_cfb_games(self) -> List[Dict]:
        """Fetch live CFB games and odds - NO DEMO FALLBACK"""
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
            
            print(f"✅ Fetched {len(processed_games)} REAL CFB games from API")
            return processed_games
            
        except Exception as e:
            print(f"❌ Failed to fetch CFB games: {e}")
            print("💡 Check your ODDS_API_KEY in .env file")
            return []  # Return empty list, NO DEMO

    def fetch_player_props(self, league: str) -> List[Dict]:
        """Fetch REAL player props - NO DEMO FALLBACK"""
        try:
            sport_key = 'americanfootball_nfl' if league == 'NFL' else 'americanfootball_ncaaf'
            url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds"
            params = {
                'apiKey': self.api_keys['odds_api'],
                'regions': 'us',
                'markets': 'player_pass_tds,player_pass_yds,player_rush_yds,player_receptions',
                'oddsFormat': 'american'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            props_data = response.json()
            processed_props = []
            
            for game in props_data:
                processed_props.extend(self.process_player_props(game, league))
            
            print(f"✅ Fetched {len(processed_props)} REAL {league} player props from API")
            return processed_props
            
        except Exception as e:
            print(f"❌ Failed to fetch {league} player props: {e}")
            print("💡 Check your ODDS_API_KEY and API limits")
            return []  # Return empty list, NO DEMO

    def process_player_props(self, game_data: Dict, league: str) -> List[Dict]:
        """Process player props data"""
        props = []
        
        try:
            for bookmaker in game_data.get('bookmakers', []):
                if 'bovada' in bookmaker.get('title', '').lower():
                    for market in bookmaker.get('markets', []):
                        for outcome in market.get('outcomes', []):
                            if 'point' in outcome:  # Has a line/total
                                prop = {
                                    'game': f"{game_data['away_team']} @ {game_data['home_team']}",
                                    'player': outcome.get('description', 'Unknown Player'),
                                    'market': market['key'],
                                    'line': outcome['point'],
                                    'odds': outcome['price'],
                                    'league': league
                                }
                                props.append(prop)
        except Exception as e:
            print(f"❌ Error processing props: {e}")
        
        return props

    def analyze_player_props(self, props: List[Dict], league: str) -> List[Dict]:
        """Analyze player props for value"""
        analyzed_props = []
        
        for prop in props:
            analysis = self.generate_prop_analysis(prop, league)
            if analysis['confidence'] >= 70:  # Only high confidence props
                analyzed_props.append(analysis)
        
        # Sort by confidence
        analyzed_props.sort(key=lambda x: x['confidence'], reverse=True)
        
        return analyzed_props[:5]  # Top 5 props

    def generate_prop_analysis(self, prop: Dict, league: str) -> Dict:
        """Generate analysis for a single player prop"""
        
        # Simulate analysis factors
        factors = {
            'matchup_advantage': random.uniform(-3, 3),
            'recent_form': random.uniform(-2, 2),
            'weather_impact': random.uniform(-1, 1),
            'injury_concerns': random.uniform(-2, 2),
            'pace_of_play': random.uniform(-1.5, 1.5),
            'game_script': random.uniform(-2, 2)
        }
        
        total_edge = sum(factors.values())
        confidence = min(abs(total_edge) * 8 + 55, 90)
        
        # Determine pick direction
        pick_direction = "OVER" if total_edge > 0 else "UNDER"
        
        reasoning = self.generate_prop_reasoning(prop, factors, pick_direction)
        
        return {
            'prop': prop,
            'pick': f"{pick_direction} {prop['line']}",
            'confidence': confidence,
            'reasoning': reasoning,
            'factors': factors
        }

    def generate_prop_reasoning(self, prop: Dict, factors: Dict, direction: str) -> str:
        """Generate reasoning for prop pick"""
        
        market = prop['market']
        player = prop['player']
        
        if 'pass_yds' in market:
            if direction == "OVER":
                return f"{player} should have a big day through the air. The matchup favors the passing game and the game script points to volume."
            else:
                return f"Expecting a run-heavy game plan. {player} likely won't need to air it out much in this spot."
        
        elif 'rush_yds' in market:
            if direction == "OVER":
                return f"{player} gets a plus matchup on the ground. Expecting them to lean on the run game in this spot."
            else:
                return f"This game script points to a passing attack. {player} won't get the volume needed to hit the over."
        
        elif 'pass_tds' in market:
            if direction == "OVER":
                return f"{player} is in a great spot to find the end zone multiple times. Red zone opportunities should be there."
            else:
                return f"Don't see the touchdown upside in this matchup. Field goals over touchdowns."
        
        elif 'receptions' in market:
            if direction == "OVER":
                return f"{player} should see heavy target share. Game script favors the passing attack."
            else:
                return f"Expecting a run-heavy approach. {player}'s targets likely limited in this game plan."
        
        return f"{direction} looks like the sharp play on {player} in this spot."

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

    def get_team_stats(self, team_name: str, league: str) -> Dict:
        """Get team stats and rankings"""
        league_key = league.lower()
        return self.team_data.get(league_key, {}).get(team_name, {
            'record': '0-0',
            'offense_rank': 16,
            'defense_rank': 16,
            'rush_offense': 16,
            'rush_defense': 16,
            'pass_offense': 16,
            'pass_defense': 16,
            'points_for': 21.0,
            'points_against': 21.0
        })

    def generate_game_analysis(self, game: Dict) -> Dict:
        """Generate elite analysis for a game with team rankings"""
        
        # Get team stats
        away_stats = self.get_team_stats(game['away_team'], game['league'])
        home_stats = self.get_team_stats(game['home_team'], game['league'])
        
        pick_data = self.calculate_advanced_pick(game, away_stats, home_stats)
        
        analysis_sections = {
            'the_line': self.generate_line_analysis(game, pick_data),
            'the_matchup': self.generate_advanced_matchup_analysis(game, pick_data, away_stats, home_stats),
            'the_angle': self.generate_angle_analysis(game, pick_data),
            'the_bottom_line': self.generate_bottom_line(game, pick_data)
        }
        
        predicted_score = self.generate_predicted_score(game, pick_data)
        
        return {
            'game_info': {
                'away_team': game['away_team'],
                'home_team': game['home_team'],
                'away_record': away_stats['record'],
                'home_record': home_stats['record'],
                'time': self.format_game_time(game['commence_time']),
                'venue': self.get_venue(game['home_team']),
                'spread': game['spread'],
                'total': game['total'],
                'away_ml': game['away_ml'],
                'home_ml': game['home_ml'],
                'away_stats': away_stats,
                'home_stats': home_stats
            },
            'pick': pick_data,
            'predicted_score': predicted_score,
            'analysis': analysis_sections
        }

    def calculate_advanced_pick(self, game: Dict, away_stats: Dict, home_stats: Dict) -> Dict:
        """Advanced pick calculation using team rankings and stats"""
        
        # Calculate ranking advantages
        off_def_edge = (home_stats['defense_rank'] - away_stats['offense_rank']) + \
                      (away_stats['defense_rank'] - home_stats['offense_rank'])
        
        rush_edge = (home_stats['rush_defense'] - away_stats['rush_offense']) + \
                   (away_stats['rush_defense'] - home_stats['rush_offense'])
        
        pass_edge = (home_stats['pass_defense'] - away_stats['pass_offense']) + \
                   (away_stats['pass_defense'] - home_stats['pass_offense'])
        
        factors = {
            'home_field_advantage': random.uniform(1.5, 3.5),
            'ranking_edge': off_def_edge * 0.2,
            'rush_matchup': rush_edge * 0.15,
            'pass_matchup': pass_edge * 0.15,
            'recent_form': random.uniform(-2, 2),
            'motivation_factor': random.uniform(-1.5, 1.5),
            'weather_impact': random.uniform(-1, 1),
            'injury_impact': random.uniform(-2, 2),
            'public_betting': random.uniform(0.3, 0.8)
        }
        
        total_edge = sum(factors.values())
        spread = game['spread']
        
        # Determine pick based on edge vs spread
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
        
        # Calculate betting units based on confidence
        confidence = min(abs(total_edge) * 8 + 60, 95)
        
        if confidence >= 85:
            units = "3U"
        elif confidence >= 75:
            units = "2U"
        else:
            units = "1U"
        
        return {
            'team': pick_team,
            'line': pick_line,
            'confidence': confidence,
            'units': units,
            'factors': factors
        }

    def generate_advanced_matchup_analysis(self, game: Dict, pick_data: Dict, away_stats: Dict, home_stats: Dict) -> str:
        """Generate advanced matchup analysis with rankings"""
        intro = random.choice(self.analysis_templates['matchup_intros'])
        
        analysis = f"{intro} "
        
        # Analyze offensive vs defensive rankings
        if away_stats['offense_rank'] < home_stats['defense_rank']:
            analysis += f"{game['away_team']} (#{away_stats['offense_rank']} offense) has a significant edge against {game['home_team']}'s #{home_stats['defense_rank']} ranked defense. "
        
        # Rush vs rush defense analysis
        rush_adv = abs(away_stats['rush_offense'] - home_stats['rush_defense'])
        if rush_adv > 10:
            if away_stats['rush_offense'] < home_stats['rush_defense']:
                analysis += f"The ground game should favor {game['away_team']} significantly. "
            else:
                analysis += f"{game['home_team']} should stuff the run effectively. "
        
        # Pass vs pass defense analysis  
        pass_adv = abs(away_stats['pass_offense'] - home_stats['pass_defense'])
        if pass_adv > 8:
            if away_stats['pass_offense'] < home_stats['pass_defense']:
                analysis += f"Through the air, {game['away_team']} has a clear advantage. "
            else:
                analysis += f"The secondary should give {game['away_team']} problems. "
        
        # Points analysis
        avg_diff = (away_stats['points_for'] - home_stats['points_against']) + \
                  (home_stats['points_for'] - away_stats['points_against'])
        
        if avg_diff > 7:
            analysis += "The offensive firepower should translate to points. "
        elif avg_diff < -7:
            analysis += "This has the makings of a defensive struggle. "
        
        return analysis

    def generate_line_analysis(self, game: Dict, pick_data: Dict) -> str:
        """Generate analysis of the betting line"""
        hook = random.choice(self.analysis_templates['opening_