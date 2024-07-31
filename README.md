# bridge-money-movement

## Architecture
### Components
Investor Account Service:
* Wraps API and encapsulates functionality for handling withdrawals from investor accounts.

Fund Account Service: 
* Wraps API for remitting funds to investment fund accounts.
* Encapsulates criteria such as minimum investment threshold and seat availability
* Potentially could pull logic into a verification engine as rules and complexity grows

Workflow Engine:
* Manages state transitions 
* Ensuring atomicity and consistency.

Tasks Runner / Async jobs
* Handles workflow tasks
* Allows for long running work, scheduling, etc..
* Can handle concurrency and tuning simultaneous runs
* Celery, Sidekiq, or built-in task queues for cloud platforms can be used.

Notification Service:
* Provides real-time updates on transaction status to relevant parties.
* Could start by just writing to an event log or table.
* Could eventually manage a variety of notification rules and outboxes--trigger SMS, webhooks, Slack, etc...

Database:
* Centralized storage for all account balances, transaction records, and logs.
* Traditional ACID relational database would be the best. For an example/test v0 we'll use sqlite.
* As noted in the problem statement, Postgres is a good way to go.

API endpoints:
* Allow access either internally or through customer-facing applications
* Handles security and authorization

Credentials Store: 
* Securely store login and access information for customer accounts.


## Workflow Engine

The heart of this application is a multi-step workflow where a single transaction passes between different states.
In each state there are unique services that need to be interacted with, and unique errors with their own resolutions.  

1. Transaction Initiation:
    * Investor or internal system initiates a transaction with a source and destination account.
    * Create records
2. Validation (multiple steps)
    * Check balance of source if available. Verify funds, verify allocation.
    * Criteria Verification: Fund Account Service verifies if the transaction meets fund criteria.
    * Reserve allocation: Prior to withdrawing funds we want to reserve allocation in the fund.
    * Expansion: this could become a more sophisticated rules engine
3. Withdrawal Processing: Investor Account Service processes the withdrawal.
    * Presumably may take a short period or may take multiple days depending on financial infrastructure
    * Could have various errors related to the client's bank which each need to be handled.
4. Fund Transfer:
    * Transaction Service completes the transfer to the fund account.
    * Could take hours to a few days for money to transfer and settle successfully
5. Mark transaction complete.
    * Mark allocation complete
6. Notification: 
    * Notification Service updates the investor and fund with the transaction status.
    * Could take place over multiple channels, each with their own failure mode and error handling
    * This is lower priority

## Technical Decisions and tradeoffs

Caching:
* Caching not done in this example.
* Could use Redis for caching frequently accessed data such as account balances, though maybe data recency via API is preferable.
* Always add caching when it's needed, not earlier

Queuing: 
* For a toy example where durability isn’t important we could just implement in memory.
* We could leverage Redis early and eventually move to a more robust queue service.
* We will want a durable queue to back the async task queue.

Database:
* Relational database like PostgreSQL for transactional consistency and integrity.

Concurrency Control:
* Use optimistic locking to handle multiple transactions and avoid race conditions.
* Can tune background workers

## Phased Development

### Example (this)



### Early working system
All the above and:
* Full versioning on models
* Allocation model

### Advanced system

As demand and complexity grows there are a number of ways we can enhance the system.
* Could become an event driven system


### Assumption: Two-Step Transfer Process
* Atomic Operations: Breaking down the process into two atomic operations (withdrawal and deposit) allows for better control over each step. If one step fails, you can handle the failure appropriately without affecting the other step.

* Separation of Concerns: It separates the logic and responsibilities of withdrawing funds from depositing funds, making the system more modular and easier to manage.

* Security: By having an intermediary step, we can perform additional checks and validations. For example, verifying the availability of funds before committing to the deposit step.

* Flexibility and Scalability: This approach makes it easier to handle complex business rules down the road and other criteria that might be associated with the withdrawal or the deposit process.

* Auditing and Logging: Each step can be logged and audited separately, providing a clearer trail for tracing transactions.

## Setup and Run

Ensure core dependencies and runtime are installed locally.
For this project we use the latest version of Python and PDM for dependency and environment management.

```
# Example on mac
$ brew install python@3.12 pdm
```

```
# Setup and install dependencies
$ make setup

# Run tests
$ make tests

# Run the application
$ make run
```

```
$ make docker-build
$ make docker-test
$ make docker-lint
$ make docker-format
```