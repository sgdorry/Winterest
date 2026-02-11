# Progress and Goals

## Progress:                                                                      
Backend Infrastructure:                                                       
- REST API backend service for managing geographic data                       
- MongoDB integration with connection management                              
- Python Anywhere deployment configuration                                    
- In-memory caching for performance                                           
- Data validation for all entities                                            
                                                                                
### Geographic Entities (Full CRUD):                                              
- Countries: Name, population, continent, capital, GDP, area, founded, president                                                                     
- States: Name, population, capital, governor, country_code, code            
- Cities: Name, population, state, state_code, area, founded, mayor           
- Counties: Name, population, state, area, founded, county_seat, state_code   
                                                                                
### REST API Endpoints:                                                                                                                
- /endpoints - API discovery                                                  
- /echo - POST testing                                                        
- /stats - Entity counts                                                      
- /countries, /states, /cities, /counties - Full CRUD for each                
                                                                                
### Development Tools:                                                            
- Makefile for build automation                                               
- Comprehensive unit tests for all modules                                     
- GitHub Actions CI/CD pipeline                                               
- Flask-RESTX API documentation (Swagger)                                     
- CORS support for frontend integration   


## Goals:

### Geography Guessing Game

### Core Pages
- Title
- Home/landing page
- Rules/how-to-play page
- Leaderboard page
- Game select
- Gameplay

### Players:
	
- Creating a player account is required to play
- Users can edit and delete their own accounts
- A history of each user’s interactions with the system is recorded (games played, scores, guesses made)
- A leaderboard will be displayed ranked by total points.
- Player statistics will be viewable on their profile

### Game Content:

- All hints and their corresponding countries/answers are stored in the database
- Each country has a series of hints that progressively reveal information
- Hints include: geographic clues, population, capital, etc.

### Gameplay:

- Players start a new game to guess a country
- Hints are progressively revealed (displayed after each incorrect guess)
- Higher points for fewer hints used (less guesses)
- Lower points for more hints used (more guesses)
- Each completed game updated the player’s total score
- Players can only see their own game history
- Leaderboard shows all players’ scores
