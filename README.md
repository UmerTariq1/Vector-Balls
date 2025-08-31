# Vector Balls

A fast-paced, real-time 2D physics-based survival game built with Python and Pygame.

## 🎮 Game Description

Vector Balls is a competitive physics simulation where players control colored balls that move within a circular arena. The objective is to be the last ball remaining by strategically removing other balls' lines while protecting your own.

## ✨ Features

- **Real-time Physics**: Smooth ball movement with realistic collisions and boundary interactions
- **Dynamic Line System**: Balls gain and lose lines that create strategic gameplay elements
- **Smart Color Assignment**: Automatic random assignment of 12 distinct colors to balls
- **Grace Period**: 1-second safety period at game start where no lines can be removed
- **Interactive Setup**: User-friendly setup screen with color picker and parameter adjustment
- **Live Scoreboard**: Real-time display of each ball's remaining lines
- **Detailed Statistics**: End-of-game stats with rankings, color identification, and performance tracking
- **Pause/Resume**: Spacebar to pause and resume gameplay anytime
- **Quit Confirmation**: ESC key with confirmation dialog to return to menu
- **Multiple Exit Options**: Exit buttons available in setup menu and stats screen
- **Customizable Settings**: Configure ball count (2-12), colors, arena size, and collision parameters

## 🚀 Installation

### Prerequisites
- Python 3.11 or higher
- pip package manager

### Setup Steps

1. **Clone or download the project files**

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🎯 How to Play

### Starting the Game

1. Run the game:
   ```bash
   python main.py
   ```

2. **Setup Screen**: Configure your game settings:
   - Number of balls (2-12)
   - Lines added per boundary hit (1-10)
   - Ball-ball collision speed increase factor
   - Boundary collision speed increase
   - Arena size percentage (30-100%)
   - Select unique colors for each ball

3. Click "Start" to begin gameplay

### Controls

#### During Gameplay
- **Spacebar**: Pause/Resume gameplay anytime
- **ESC**: Show quit confirmation dialog (returns to menu if confirmed)
- **R**: Return to setup menu (only when game is over)

#### Setup Menu
- **Mouse**: Click settings, color picker, Start/Exit buttons
- **ESC**: Exit the application
- **Enter**: Confirm selections

#### Stats Screen
- **R**: Return to setup menu
- **Mouse**: Click Exit Game button to quit application

### Gameplay Mechanics

#### Ball Movement
- Balls move continuously within the circular arena
- Physics-based collisions with realistic bouncing

#### Line System
- Each ball starts with 3 lines anchored to random boundary points
- Lines grow and shrink as balls move
- Lines cannot be interacted with by their own ball

#### Grace Period
- First 1 second of gameplay: No lines can be removed (safety period)
- Visual countdown shows remaining time: "Peace time remaining: 0.8s"
- Allows players to get oriented and positioned before competitive phase begins

#### Interactions
- **Ball-Ball Collision**: Balls bounce off each other with increased speed
- **Ball-Boundary Collision**: Balls bounce off the arena wall and gain new lines
- **Ball-Line Collision**: Touching another ball's line removes that line permanently

#### Color Assignment
- 12 distinct colors available: Red, Green, Blue, Yellow, Magenta, Cyan, Orange, Purple, Gold, Hot Pink, Navy Blue, Dark Magenta
- Automatic random assignment ensures each ball gets a unique, easily distinguishable color
- Colors are optimized for maximum visual distinction

#### Victory Conditions
- A ball is eliminated when all its lines are removed
- Last remaining ball wins
- Game continues until only one ball remains

### Strategy Tips

- **Offensive Play**: Position yourself to intersect opponents' lines
- **Defensive Play**: Avoid letting opponents get near your lines
- **Boundary Usage**: Use boundary bounces to gain new lines strategically
- **Speed Management**: Faster balls can cover more ground but are harder to control

## ⚙️ Configuration

The game offers extensive customization through the setup screen:

### Core Settings
- **Ball Count**: 2-12 balls (default: 6)
- **Lines per Boundary Hit**: 1-10 lines added when hitting boundary (default: 3)
- **Collision Speed Factors**: Control speed increases after collisions
- **Arena Size**: 30-100% of default size (default: 100%)

### Visual Settings
- **Color Selection**: Choose unique colors for each ball from a palette
- **Window Size**: Fixed at 1000x1000 pixels
- **Frame Rate**: 60 FPS for smooth gameplay

### Advanced Physics
- **Boundary Bounce**: Configurable speed increase on wall hits
- **Ball-Ball Interactions**: Adjustable speed boosts after collisions
- **Line Anchoring**: Fixed boundary attachment points

## 📊 Statistics

At the end of each game, view comprehensive statistics on a clean, separate screen:

### Rankings System
- **🏆 1st Place**: Winner with trophy emoji and gold color
- **🥈 2nd Place**: Silver medal
- **🥉 3rd Place**: Bronze medal
- **4th+ Places**: Ordinal rankings
- Shows top 5 performers with ball numbers and colors

### Performance Metrics
- **Color Identification**: Visual color squares next to each ball's stats
- **Lines Removed**: How many enemy lines each ball destroyed (offensive score)
- **Lines Lost**: How many of each ball's own lines were removed (defensive score)
- **Ball Elimination Order**: Complete ranking of when each ball was eliminated

### Visual Design
- **Clean Layout**: Separate stats screen eliminates background interference
- **Color Coding**: Each ball's stats include its actual color square
- **Easy Navigation**: R key returns to setup menu, Exit button quits application

## 🛠️ Technical Details

### Architecture
- **main.py**: Entry point, setup UI, quit confirmation, and main game loop
- **game.py**: Game state management, rendering, and grace period logic
- **ball.py**: Ball entity with physics and line management
- **physics.py**: Collision detection, color matching, and physics utilities
- **config.py**: Global constants, color palette, and default settings
- **settings.py**: Runtime configuration management

### Key Technologies
- **Pygame**: 2D graphics, input handling, and game framework
- **Real-time Physics**: Custom collision detection and response system
- **Color Management**: 12 optimized colors with automatic assignment
- **UI System**: Interactive setup screen with mouse and keyboard support


## 🎨 Customization

### Color Management
- **Current Palette**: 12 optimized colors (Red, Green, Blue, Yellow, Magenta, Cyan, Orange, Purple, Gold, Hot Pink, Navy Blue, Dark Magenta)
- **Adding Colors**: Modify both `COLORS` in `config.py` and `COLOR_NAMES` in `physics.py` to maintain synchronization
- **Color Matching**: Physics engine automatically finds closest color name for stats display

### Game Parameters
- **Ball Count**: 2-12 balls (default: 6)
- **Arena Size**: 30-100% of default (default: 75%)
- **Lines per Hit**: 1-10 lines added on boundary collision (default: 3)
- **Speed Factors**: Collision speed increases (default: 0.12 for ball-ball, 25.0 for boundary)
- **Grace Period**: 1-second safety period (configurable in `config.py`)

### Physics Tuning
```python
# Key values in config.py
BALL_COLLISION_SPEED_INCREASE_FACTOR = 0.12
BOUNDARY_COLLISION_SPEED_INCREASE = 25.0
GRACE_PERIOD_DURATION = 1.0
INITIAL_SPEED_MIN = 160.0
INITIAL_SPEED_MAX = 240.0
```

### UI Customization
- **Fonts**: Modify `FONT_NAME` in `config.py`
- **Colors**: Update background and UI element colors
- **Layout**: Adjust button positions and spacing in setup screen

## 🔧 System Requirements

- **OS**: Windows 10+, macOS 10.12+, Linux
- **Python**: 3.11 or higher
- **RAM**: 512MB minimum
- **Display**: 1024x768 minimum resolution
- **Input**: Mouse and keyboard required

## 🎮 Tips & Strategies

### Beginner Tips
- Use the grace period to position yourself advantageously
- Stay near the boundary to gain lines quickly
- Watch for balls approaching your lines from behind

### Advanced Strategies
- Time your boundary bounces to create line barriers
- Use speed boosts strategically for quick maneuvers
- Position yourself to intercept multiple opponents' lines simultaneously

### Performance Notes
- Optimal performance with 2-8 balls
- Higher ball counts (9-12) may require more powerful hardware
- 60 FPS gameplay for smooth physics simulation

## 🐛 Troubleshooting

- **Emojis not showing**: Some systems may not display emoji characters in game text
- **Color similarity**: If colors appear too similar, they can be manually reselected in setup
- **Performance issues**: Reduce ball count or arena size for better performance

## 📄 License

This project is open source and available under the MIT License.

---

**Enjoy Vector Balls!** May the best ball win! 🏆
