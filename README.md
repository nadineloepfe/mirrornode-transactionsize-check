# Mirrornode Transaction size check

This repository is designed to identify large transactions (>5KB) on the Hedera network. It does this through analysing the /transaction endpoint.


## Code Explanation

### Sequential Operations
Large transactions (>5kb) involve a series of related operations rather than isolated actions. For instance, creating a file, appending multiple data chunks to it, performing Ethereum transactions, and then deleting the file.

The script processes transactions by fetching them from the Hedera Testnet Mirror Node API. It analyses them to detect sequences that contain:

- FILECREATE: Marks the start of a file operation.
- FILEAPPEND: Adds chunks of data.
- ETHEREUMTRANSACTION: An Ethereum-related transaction.
- FILEDELETE: Marks the end of a file operation.

### Shared entity_id:
The script also ensures that these operations all share the same entity_id (file_id) to accurately group related transactions.
This association indicates that the transactions are part of a single, cohesive operation rather than disparate actions.


## Chunk Breakdown

Big transactions (those involving file operations) are categorised by how many chunks (FILEAPPEND operations) they contain. The breakdown groups transactions with more than 10 chunks into a single category (>10 Chunks).


## Code Structure

### fetch_transactions(account_id)

Fetches all transactions for the specified account from the Hedera Testnet Mirror Node.
Filters the transactions initiated by the account.

### process_transactions(all_transactions)

Processes all fetched transactions.
Detects big and small transactions.

### collect_sequence(start_index, all_transactions)

Collects transactions and checks for file operations.

### is_valid_big_transaction(sequence)

Checks if the sequence contains the required file operations (FILECREATE, FILEAPPEND, ETHEREUMTRANSACTION, FILEDELETE) and ensures they occur in the correct order.


#### Example Output

```
INFO: Fetching transactions for account: 0.0.xxx
INFO: Total transactions fetched: 1400
INFO: 7040 transactions initiated by account 0.0.xxx.

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

Statistics:
Big Transactions: 6.73%
Small Transactions: 93.27%
```

## How to Use

1) Clone this repository.

2) Rename .env.sample to .env and add the Hedera account ID as well as the chosen environment (testnet, mainnet..):

```
ACCOUNT_ID=0.0.xxxxxxx
ENVIRONMENT=testnet
```

3) Replace 0.0.xxxxxxx with your Hedera account ID.

4) Run the get_statistics.py script located at the root level to get an insight of large transactions.

```
python get_statistics.py
```


## Dependencies

Make sure to install the necessary dependencies by running:

```
pip install -r requirements.txt
```

