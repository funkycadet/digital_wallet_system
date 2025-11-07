# Digital Wallet Transaction System

A simple digital wallet system that demonstrates how PostgreSQL and Kafka can work together in a microservices architecture. Users can create wallets, add money, and transfer funds. The transaction history is built asynchronously through Kafka events.

This project is designed to illustrate concepts like PostgreSQL transactions, Kafka producer/consumer patterns, and eventual consistency.

## Architecture

The system consists of two main services, a Kafka message broker, and a shared PostgreSQL database.

```plaintext
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│  Wallet Service │───▶│    Kafka     │───▶│ History Service │
│    (Django)     │    │              │    │    (Django)     │
└─────────────────┘    │wallet_events │    └────────────────┘
         │             └──────────────┘             │
         └──────────────────────────────────────────┘
                   Shared PostgreSQL Database
```

**Flow:**
1.  A client interacts with the Wallet Service API.
2.  The Wallet Service updates the database immediately within a transaction.
3.  Upon a successful transaction, the Wallet Service publishes an event to a Kafka topic.
4.  The History Service consumes the event from Kafka and updates its own tables.
5.  The client can query the History Service to get a user's transaction history.

## Tech Stack

-   **Backend**: Django + Django Rest Framework
-   **Database**: PostgreSQL
-   **Messaging**: Apache Kafka
-   **Infrastructure**: Docker Compose

## Services

### Wallet Service
-   Manages user wallets (creation, funding, transfers).
-   Handles synchronous balance updates.
-   Publishes events to Kafka for any state change.

### History Service
-   Provides an audit trail of all transactions.
-   Listens for wallet events from Kafka.
-   Stores transaction history and provides an API to query it.
-   Designed to handle duplicate events gracefully.

## Getting Started

### Prerequisites
-   Docker
-   Docker Compose

### Setup
1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd digital_wallet_transaction_system
    ```

2.  **Set up environment variables:**
    Copy the example environment file and update it if necessary.
    ```bash
    cp .env.example .env
    ```

3.  **Build and run the services:**
    ```bash
    docker-compose up --build
    ```
    This will start the Wallet Service, History Service, PostgreSQL database, Kafka, and Zookeeper.

4.  **Create the Kafka topic:**
    Once the containers are running, open a new terminal and run the following command to create the `wallet_events` topic:
    ```bash
    docker-compose exec history_service python manage.py create_topic
    ```

The services will be available at:
-   **Wallet Service**: `http://localhost:8000`
-   **History Service**: `http://localhost:8001`

## API Endpoints

### Wallet Service (`localhost:8000`)
-   `POST /wallets/`: Create a wallet for a user.
-   `POST /wallets/{wallet_id}/fund/`: Add funds to a wallet.
-   `POST /wallets/{wallet_id}/transfer/`: Transfer funds to another wallet.
-   `GET /wallets/{wallet_id}/`: Get wallet balance.
-   `GET /users/{user_id}/wallets/`: List all wallets for a user.

### History Service (`localhost:8001`)
-   `GET /wallets/{wallet_id}/history/`: Get the transaction history for a specific wallet.
-   `GET /users/{user_id}/activity/`: Get all activity for a user.

## Database Design

The system uses a single PostgreSQL database with three main tables.

```sql
-- Owned by Wallet Service
CREATE TABLE wallets (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    balance DECIMAL(19,4) NOT NULL DEFAULT 0,
    version BIGINT NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE wallet_transactions (
    id VARCHAR(36) PRIMARY KEY,
    wallet_id VARCHAR(36) NOT NULL REFERENCES wallets(id),
    amount DECIMAL(19,4) NOT NULL,
    type VARCHAR(20) NOT NULL, -- 'FUND', 'TRANSFER_OUT', 'TRANSFER_IN'
    status VARCHAR(20) NOT NULL, -- 'COMPLETED', 'FAILED'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Owned by History Service
CREATE TABLE transaction_events (
    id VARCHAR(36) PRIMARY KEY,
    wallet_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(100) NOT NULL,
    amount DECIMAL(19,4) NOT NULL,
    event_type VARCHAR(30) NOT NULL,
    transaction_id VARCHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    event_data JSONB
);
```

## Business Rules
-   Users are identified by a string ID (no authentication).
-   Wallet balances cannot be negative.
-   All monetary values use 4 decimal places.
-   Balance updates are immediate and transactional.
-   History updates are eventual and driven by events.
