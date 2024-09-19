# Check Function Parameter Size 

This Python script fetches and analyzes Hedera CONTRACTCALL and CONTRACTCREATEINSTANCE transactions for a specific account, and checks the size of function_parameters for each transaction. The goal is to identify transactions where the function_parameters size exceeds 5kb.
Features

- Fetches CONTRACTCALL and CONTRACTCREATEINSTANCE transactions for a given Hedera account.
- Analyses the size of function_parameters for each transaction.
- Classifies transactions based on whether their function_parameters are over or under 5kb.
- Displays the maximum function_parameters size encountered.

## Prerequisites

- Python 3.6+
- requests module (for making HTTP requests)
- python-dotenv module (for loading environment variables from a .env file)


## Install

To install the required modules, run:

```
pip install requests python-dotenv
```
or 
```
pip install -r requirements.txt
```

## Setup

1) Clone the repository or create the script with the provided Python code.

2) rename .env.sample to .env and add your Hedera account ID:

2) Rename .env.sample to .env and add the Hedera account ID as well as the chosen environment (testnet, mainnet..):

```
ACCOUNT_ID=0.0.xxxxxxx
ENVIRONMENT=testnet
```

3) Replace 0.0.xxxxxxx with your Hedera account ID.

4) Run the script by executing the following command:

```
python check_function_param_size.py
```

## Script Workflow

- Load Environment Variables: 
    The script uses python-dotenv to load the ACCOUNT_ID from the .env file.

- Fetch Transactions:
    It queries the Hedera Mirror Node API to fetch all CONTRACTCALL and CONTRACTCREATEINSTANCE transactions for the given account.
    If there are more than 100 transactions, pagination is handled to fetch additional transactions.

- Analyze Transactions:
    For each transaction, the function_parameters field is fetched from the contracts/results API endpoint.
    If function_parameters exists, its size is calculated and classified as either over or under 5KB.

- Output Results:
    The script outputs the total number of transactions fetched, how many had function_parameters larger than 5KB, and how many were under 5KB.
    It also prints the maximum size of function_parameters encountered during the analysis.


## Example Output

```
Fetching CONTRACTCALL and CONTRACTCREATEINSTANCE transactions for account: 0.0.xxxxxxx
Fetching URL: https://testnet.mirrornode.hedera.com/api/v1/transactions?account.id=0.0.xxxxxxx&transactiontype=CONTRACTCALL&limit=100&order=asc
Fetching URL: https://testnet.mirrornode.hedera.com/api/v1/transactions?account.id=0.0.xxxxxxx&transactiontype=CONTRACTCREATEINSTANCE&limit=100&order=asc
Total CONTRACTCALL and CONTRACTCREATEINSTANCE transactions fetched: 200
Maximum function_parameters size: 7100 bytes

Analysis for account 0.0.xxxxxxx:
Transactions over 5kb (function_parameters > 5kb): 5
Transactions under 5kb (function_parameters <= 5kb): 195
```

## Error Handling

The script catches errors during API calls and prints the error message without terminating the entire process. This ensures that the script continues to fetch and analyze other transactions even if some fail.

## Notes

- The size of function_parameters is calculated after removing the 0x prefix (if present).
- Only valid hexadecimal strings are considered; invalid strings are marked as transactions with function_parameters under 5KB.
- The Mirror Node API is queried for CONTRACTCALL and CONTRACTCREATEINSTANCE transactions separately, but both are included in the analysis.


## License 
This project is open-source and available for modification and distribution.