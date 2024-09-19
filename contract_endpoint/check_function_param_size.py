import requests
import urllib.parse
import os
from dotenv import load_dotenv

def check_function_param_size(account_id):
    base_url = 'https://testnet.mirrornode.hedera.com'

    # fetch CONTRACTCALL and CONTRACTCREATEINSTANCE transactions
    urls = [
        f"{base_url}/api/v1/transactions?account.id={account_id}&transactiontype=CONTRACTCALL&limit=100&order=asc",
        f"{base_url}/api/v1/transactions?account.id={account_id}&transactiontype=CONTRACTCREATEINSTANCE&limit=100&order=asc"
    ]

    transaction_ids = []
    total_transactions_fetched = 0

    print(f"Fetching CONTRACTCALL and CONTRACTCREATEINSTANCE transactions for account: {account_id}")

    # fetch transactions and handle pagination
    for url in urls:
        while url:
            try:
                print(f"Fetching URL: {url}")
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()
                transactions = data.get('transactions', [])

                total_transactions_fetched += len(transactions)

                # get tx ids
                for tx in transactions:
                    transaction_id = tx.get('transaction_id')
                    transaction_ids.append(transaction_id)

                # pagination
                next_link = data.get('links', {}).get('next')
                url = f"{base_url}{next_link}" if next_link else None
            except Exception as e:
                print('Error fetching transactions:', str(e))
                break

    print(f"Total CONTRACTCALL and CONTRACTCREATEINSTANCE transactions fetched: {total_transactions_fetched}")

    over_5kb_count = 0
    under_5kb_count = 0
    data_sizes = []

    # Fetch contract results for each tx
    for transaction_id in transaction_ids:
        encoded_transaction_id = urllib.parse.quote(transaction_id, safe='')
        contract_result_url = f"{base_url}/api/v1/contracts/results/{encoded_transaction_id}"

        try:
            contract_result_response = requests.get(contract_result_url)
            contract_result_response.raise_for_status()
            contract_result = contract_result_response.json()

            # get function_parameters
            function_params_hex = contract_result.get('function_parameters')
            if not function_params_hex:
                under_5kb_count += 1  # mark as under 5kb if function_parameters is missing
                continue

            # remove '0x' prefix if present
            if function_params_hex.startswith('0x') or function_params_hex.startswith('0X'):
                function_params_hex = function_params_hex[2:]

            # check that string contains only valid hex characters
            if all(c in '0123456789abcdefABCDEF' for c in function_params_hex):
                function_params_bytes = bytes.fromhex(function_params_hex)
                data_size = len(function_params_bytes)
                data_sizes.append(data_size)

                # check if the size is over 5kb 
                if data_size > 5 * 1024:
                    over_5kb_count += 1
                else:
                    under_5kb_count += 1
            else:
                under_5kb_count += 1
                continue
        except Exception as e:
            print(f"Error fetching contract result for transaction {transaction_id}: {str(e)}")
            continue

    if data_sizes:
        max_size = max(data_sizes)
        print(f"Maximum function_parameters size: {max_size} bytes")
    else:
        print("No function_parameters data found.")

    print(f"\nAnalysis for account {account_id}:")
    print(f"Transactions over 5kb (function_parameters > 5kb): {over_5kb_count}")
    print(f"Transactions under 5kb (function_parameters <= 5kb): {under_5kb_count}")


if __name__ == "__main__":
    # load from .env file
    load_dotenv()
    account_id = os.environ.get('ACCOUNT_ID')

    if not account_id:
        print("Error: ACCOUNT_ID environment variable not set.")
        sys.exit(1)

    check_function_param_size(account_id)