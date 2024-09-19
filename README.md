# Mirrornode Transaction size check

This repository is designed to identify large transactions (>5KB) on the Hedera network. It does this through two primary endpoints: /transaction and /contract.


## Overview

### Transaction Endpoint (transaction_endpoint)
The script checks for file operations (FILEUPDATE, FILEAPPEND, FILEDELETE) that typically accompany large Ethereum transactions. It ensures that the transactions associated with these operations share the same entity_id, signifying a cohesive transaction flow.

### Contract Endpoint (contract_endpoint)
The script evaluates the function_parameters size of CONTRACTCALL or CONTRACTCREATEINSTANCE transactions, identifying those exceeding 5KB, which can indicate large or complex contract operations.

### Root-Level Script (get_stats.py)
This script runs both the transaction and contract endpoint scripts, gathers the data, and calculates the statistics for both endpoints. It provides a comprehensive view of large transactions across different types of operations on Hedera.

#### Example Output
s
```
Starting the process...

Running check_function_param_size.py...

Running find_sequence_pattern.py...
(This could take some time. Get a coffee.)

Total Transactions:
Ethereum Transactions -> /transactions endpoint: 150
Contract Transactions -> /contract endpoint: 80

Transactions over 5KB:
Ethereum Transactions -> /transactions endpoint: 90
Contract Transactions -> /contract endpoint: 35

Transactions under 5KB:
Ethereum Transactions -> /transactions endpoint: 60
Contract Transactions -> /contract endpoint: 45

---------------------------------------
              Statictics
---------------------------------------

>5kb Transactions:
Ethereum Transactions -> /transactions endpoint: 60.00%
Contract Transactions -> /contract endpoint: 43.75%

<5kb Transactions:
Ethereum Transactions -> /transactions endpoint: 40.00%
Contract Transactions -> /contract endpoint: 56.25%
```

## How to Use

1) Clone this repository.

2) Rename .env.sample to .env and add the Hedera account ID as well as the chosen environment (testnet, mainnet..):

```
ACCOUNT_ID=0.0.xxxxxxx
ENVIRONMENT=testnet
```

3) Replace 0.0.xxxxxxx with your Hedera account ID.

4) Run the get_stats.py script located at the root level to get an insight of large transactions.

```
python get_stats.py
```


## Dependencies

Make sure to install the necessary dependencies by running:

```
pip install -r requirements.txt
```
