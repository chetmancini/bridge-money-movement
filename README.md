# bridge-money-movement

## Architecture
### Components
Investor Account Service:
* Wraps API and encapsulates functionality for handling withdrawals from investor accounts.

Fund Account Service: 
* Wraps API for remitting funds to investment fund accounts.
* Encapsulates criteria such as minimum investment threshold and seat availability
* Potentially could pull logic into a verification engine as rules and complexity grows

Transaction Service:
* Manages the overall transaction process, ensuring atomicity and consistency.

Notification Service:
* Provides real-time updates on transaction status to relevant parties.
* Could start by just writing to an event log or table.
* Could eventually manage a variety of notification rules and outboxes--trigger SMS, webhooks, Slack, etc...

Database:
* Centralized storage for all account balances, transaction records, and logs.
* Traditional ACID relational database would be the best. As noted in the problem statement, Postgres is a good way to go.

Security Layer: Ensures secure communication and data integrity.

## General Flow
1. Transaction Initiation: Investor or internal system initiates a transaction with a source and destination account.
2. Validation. Check balance of source if available. Verify funds, verify allocation.
3. Withdrawal Processing: Investor Account Service processes the withdrawal.
Criteria Verification: Fund Account Service verifies if the transaction meets fund criteria.
4. Fund Transfer: Transaction Service completes the transfer to the fund account.
5. Mark transaction complete.
6. Notification: Notification Service updates the investor and fund with the transaction status.

Technical Decisions

Caching:
Use Redis for caching frequently accessed data such as account balances to improve performance.
Queuing:
Use RabbitMQ or AWS SQS to handle multiple transactions simultaneously and ensure they are processed in order. For a toy example where durability isn’t important we could just implement in Python.
Database:
Relational database like PostgreSQL for transactional consistency and integrity.
Concurrency Control: 
Use optimistic locking to handle multiple transactions and avoid race conditions.


### Advantages of Two-Step Transfer Process
* Atomic Operations: Breaking down the process into two atomic operations (withdrawal and deposit) allows for better control over each step. If one step fails, you can handle the failure appropriately without affecting the other step.

* Separation of Concerns: It separates the logic and responsibilities of withdrawing funds from depositing funds, making the system more modular and easier to manage.

* Security: By having an intermediary step, we can perform additional checks and validations. For example, verifying the availability of funds before committing to the deposit step.

* Flexibility and Scalability: This approach makes it easier to handle complex business rules down the road and other criteria that might be associated with the withdrawal or the deposit process.

* Auditing and Logging: Each step can be logged and audited separately, providing a clearer trail for tracing transactions.
