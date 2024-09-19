
This Python script analyses Ethereum transactions on the Hedera Testnet, identifying and classifying transactions into large ("big transactions") and small categories. It determines whether a transaction includes specific file operations such as FILECREATE, FILEAPPEND, ETHEREUMTRANSACTION, and FILEDELETE, and whether they occur within a specified 30-second time window.
Features

- Retrieves and processes all transactions for a specific Hedera Testnet account.
- Identifies transactions larger than 5kb by analysing sequences of file operations.
- Categorises big transactions based on the number of file append operations (chunks).
- Ensures that file operations occur in the correct order (FILECREATE → FILEAPPEND → ETHEREUMTRANSACTION → FILEDELETE).

## Prerequisites

Python 3.x

Install the required package:

```
pip install requests
```

## How to Use

    Clone the repository or copy the script into your project:
```
git clone https://github.com/nadineloepfe/mirrornode-transactionsize-check.git
```

Run the script using your Hedera account ID:

```
python find_sequence_pattern.py
```

Replace the account ID in the script with your own Hedera Testnet account ID:

```
find_sequence_pattern('0.0.yourAccountID')
```

## Code Explanation

The script processes transactions by fetching them from the Hedera Testnet Mirror Node API. It analyses them to detect sequences that contain:

- FILECREATE: Marks the start of a file operation.
- FILEAPPEND: Adds chunks of data.
- ETHEREUMTRANSACTION: An Ethereum-related transaction.
- FILEDELETE: Marks the end of a file operation.

The script ensures that these operations happen within a 30-second window and in the correct order.


## Chunk Breakdown

Big transactions (those involving file operations) are categorised by how many chunks (FILEAPPEND operations) they contain. The breakdown groups transactions with more than 10 chunks into a single category (>10 Chunks).


## Output

The script provides a summary of the analysis:

- Total Ethereum transactions: The number of Ethereum transactions found.
- Big transactions: Transactions involving file operations, categorized by chunk count.
- Small transactions: Ethereum transactions without file operations.


## Example Output

```
Fetching transactions for account: 0.0.xxx
Total transactions fetched: 1400

Analysis for account 0.0.xxx:
Total Ethereum transactions: 7040
Ethereum transactions with file operations (big transactions): 474
Ethereum transactions without file operations (small transactions): 6566

Big Transaction Sequences Breakdown:
1 Chunks: 9
2 Chunks: 120
3 Chunks: 43
4 Chunks: 52
5 Chunks: 16
6 Chunks: 49
7 Chunks: 113
8 Chunks: 27
9 Chunks: 16
10 Chunks: 12
>10 Chunks: 17
```

## Code Structure

### fetch_transactions(account_id)

Fetches all transactions for the specified account from the Hedera Testnet Mirror Node.
Filters the transactions initiated by the account.

### process_transactions(all_transactions, time_window=30)

Processes all fetched transactions.
Detects big and small transactions.
Ensures the correct sequence and time frame for big transactions.

### collect_sequence(start_index, all_transactions, time_window)

Collects transactions within the specified time window and checks for file operations.

### is_valid_big_transaction(sequence)

Checks if the sequence contains the required file operations (FILECREATE, FILEAPPEND, ETHEREUMTRANSACTION, FILEDELETE) and ensures they occur in the correct order.