# AI Trade Game - Java Version

AI-powered cryptocurrency trading system implemented in Java with Spring Boot.

## Project Structure

```
src/
├── main/
│   ├── java/com/example/
│   │   ├── AITradeGameApplication.java    # Main application class
│   │   ├── config/                        # Configuration classes
│   │   │   ├── AppConfig.java             # Application configuration
│   │   │   └── DataInitializer.java       # Data initialization
│   │   ├── controller/                    # REST controllers
│   │   │   └── TradingController.java     # Trading API endpoints
│   │   ├── entity/                        # JPA entities
│   │   │   ├── AccountValue.java          # Account value entity
│   │   │   ├── Conversation.java          # Conversation entity
│   │   │   ├── Model.java                 # Trading model entity
│   │   │   ├── Portfolio.java             # Portfolio entity
│   │   │   ├── Provider.java              # Data provider entity
│   │   │   ├── Settings.java              # Settings entity
│   │   │   └── Trade.java                 # Trade entity
│   │   ├── repository/                    # JPA repositories
│   │   │   ├── AccountValueRepository.java
│   │   │   ├── ConversationRepository.java
│   │   │   ├── ModelRepository.java
│   │   │   ├── PortfolioRepository.java
│   │   │   ├── ProviderRepository.java
│   │   │   ├── SettingsRepository.java
│   │   │   └── TradeRepository.java
│   │   ├── scheduler/                     # Scheduled tasks
│   │   │   └── TradingScheduler.java      # Trading scheduler
│   │   └── service/                       # Business logic services
│   │       ├── AITraderService.java       # AI trading service
│   │       ├── DatabaseService.java       # Database service
│   │       ├── MarketDataService.java     # Market data service
│   │       └── TradingEngineService.java  # Trading engine service
│   └── resources/
│       ├── application.properties         # Application configuration
│       └── data/                          # Data directory (created on runtime)
└── test/                                  # Test classes
```

## Prerequisites

- Java 17 or higher
- Maven 3.6 or higher
- OpenAI API key (for AI trading decisions)

## Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd java-version
   ```

2. **Configure OpenAI API key:**
   Set your OpenAI API key as an environment variable:
   ```bash
   export OPENAI_API_KEY=your_openai_api_key_here
   ```
   
   Or update the `application.properties` file:
   ```properties
   openai.api.key=your_openai_api_key_here
   ```

3. **Build the project:**
   ```bash
   mvn clean install
   ```

## Running the Application

1. **Start the application:**
   ```bash
   mvn spring-boot:run
   ```
   
   Or:
   ```bash
   java -jar target/ai-trade-game-1.0.0.jar
   ```

2. **Access the application:**
   - API endpoints: `http://localhost:8080/api/`
   - The application will automatically initialize with default data

## API Endpoints

- `GET /api/providers` - Get all providers
- `POST /api/providers` - Add a new provider
- `DELETE /api/providers/{id}` - Delete a provider
- `GET /api/models` - Get all models
- `POST /api/models` - Add a new model
- `DELETE /api/models/{id}` - Delete a model
- `GET /api/portfolio/{modelId}` - Get portfolio for a model
- `GET /api/trades/{modelId}` - Get trade history for a model
- `GET /api/conversations/{modelId}` - Get conversation history for a model
- `GET /api/account-values/{modelId}` - Get account value history for a model
- `POST /api/trade/{modelId}` - Execute a trading cycle for a model
- `GET /api/status` - Get system status

## Scheduled Trading

The application automatically executes trading cycles for all models every hour. You can modify the schedule in `TradingScheduler.java`.

## Database

The application uses SQLite as the database. The database file `trading_game.db` will be created automatically when the application starts.

## Configuration

Key configuration options in `application.properties`:

- `server.port` - Server port (default: 8080)
- `openai.api.key` - OpenAI API key
- `openai.model` - OpenAI model to use (default: gpt-3.5-turbo)
- `openai.temperature` - Temperature for OpenAI responses (default: 0.7)