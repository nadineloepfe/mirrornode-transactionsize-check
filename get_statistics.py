import requests
import os
import sys
import logging
from dotenv import load_dotenv

# configure logging
logging.basicConfig(level=logging.INFO)

def find_sequence_pattern(account_id):
    environment = os.getenv("ENVIRONMENT")
    if not environment:
        logging.error("ENVIRONMENT environment variable not set.")
        sys.exit(1)
    base_url = f'https://{environment}.mirrornode.hedera.com'
    url = f'{base_url}/api/v1/transactions?account.id={account_id}&limit=500'

    all_transactions = []

    logging.info(f'Fetching transactions for account: {account_id}')
    logging.info(f'This might take a while. Set logging level to DEBUG for more detailed real-time feedback.')

    # fetch all tx by account
    while url:
        try:
            logging.debug(f'Fetching URL: {url}')
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            transactions = data['transactions']

            # only keep tx initiated by the account
            for tx in transactions:
                tx_account = tx['transaction_id'].split('-')[0]
                if tx_account != account_id:
                    continue

                # store transactions timestamp and type
                all_transactions.append({
                    'timestamp': float(tx['consensus_timestamp']),
                    'type': tx['name'],
                    'entity_id': tx.get('entity_id')
                })

            # pagination
            next_link = data['links'].get('next')
            url = f"{base_url}{next_link}" if next_link else None

        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching transactions: {e}")
            break
        except ValueError as e:
            logging.error(f"Error parsing JSON response: {e}")
            break

    logging.info(f'Total transactions fetched: {len(all_transactions)}')

    # process transactions
    total_ethereum_transactions, big_transactions, small_transaction_count = process_transactions(all_transactions)

    # output results
    big_transaction_count = sum(big_transactions.values())

    print(f'\nAnalysis for account {account_id}:')
    print(f'Total Ethereum transactions: {total_ethereum_transactions}')
    print(f'Ethereum transactions with file operations (big transactions): {big_transaction_count}')
    print(f'Ethereum transactions without file operations (small transactions): {small_transaction_count}')

    logging.info('\nBig Transaction Sequences Breakdown:')
    sorted_chunks = sorted(big_transactions.items(), key=lambda x: int(x[0].split(' ')[0]) if x[0][0].isdigit() else 11)
    for chunk_key, count in sorted_chunks:
        logging.info(f'{chunk_key}: {count}')

    # Calculate and print statistics
    calculate_and_print_statistics(total_ethereum_transactions, big_transaction_count, small_transaction_count)

def process_transactions(all_transactions):
    """
    Process transactions to identify big and small Ethereum transactions.
    """
    # sort tx by timestamp
    all_transactions.sort(key=lambda tx: tx['timestamp'])

    # initialise counters and trackers
    total_ethereum_transactions = 0
    big_transactions = {}          # stores counts of big transactions by number of chunks
    small_transaction_count = 0    # counts small ethereum transactions
    processed_indices = set()      # tracks indices of transactions already processed
    first_sequence_printed = False

    # process big transactions first
    for i, tx in enumerate(all_transactions):
        if i in processed_indices:
            continue
        if tx['type'] == 'FILECREATE':
            # collect a big transaction sequence
            sequence, indices = collect_sequence(i, all_transactions)
            if sequence:
                is_valid, append_count = is_valid_big_transaction(sequence)
                if is_valid:
                    # validate transaction found
                    total_ethereum_transactions += 1
                    processed_indices.update(indices)
                    # categorise by chunk count
                    chunk_key = f'{append_count} Chunks' if append_count <= 10 else '>10 Chunks'
                    big_transactions[chunk_key] = big_transactions.get(chunk_key, 0) + 1

                    # check to see how sequence looks like
                    if not first_sequence_printed:
                        logging.info("\nFirst big transaction sequence found (for sanity check):")
                        for seq_tx in sequence:
                            logging.info(f"Timestamp: {seq_tx['timestamp']}, Type: {seq_tx['type']}, Entity ID: {seq_tx.get('entity_id')}")
                        first_sequence_printed = True

    # process remaining ethereum transactions not part of big transactions
    for i, tx in enumerate(all_transactions):
        if i not in processed_indices and tx['type'] == 'ETHEREUMTRANSACTION':
            # add if transaction wasn't already processed as part of a big transaction
            total_ethereum_transactions += 1
            small_transaction_count += 1
            processed_indices.add(i)

    return total_ethereum_transactions, big_transactions, small_transaction_count

def collect_sequence(start_index, all_transactions):
    """
    Collects a sequence of transactions starting from a FILECREATE,
    grouping by entity_id.
    """
    sequence = []
    indices = []
    n = len(all_transactions)
    file_entity_id = all_transactions[start_index]['entity_id']

    if not file_entity_id:
        # cannot proceed without a valid entity_id
        return [], []

    append_count = 0

    for i in range(start_index, n):
        tx = all_transactions[i]

        # skip transactions with None entity_id
        if tx['type'] in ['FILEAPPEND', 'FILEDELETE'] and not tx['entity_id']:
            continue

        # check file operations have the same entity_id
        if tx['type'] in ['FILEAPPEND', 'FILEDELETE']:
            if tx['entity_id'] != file_entity_id:
                continue

        sequence.append(tx)
        indices.append(i)

        if tx['type'] == 'FILEAPPEND':
            append_count += 1
        elif tx['type'] == 'FILEDELETE':
            break

    return sequence, indices

def is_valid_big_transaction(sequence):
    """
    Checks if a given sequence is a valid big transaction (has FILECREATE, FILEAPPEND, ETHEREUMTRANSACTION, FILEDELETE).
    """
    types_in_sequence = [tx['type'] for tx in sequence]
    append_count = types_in_sequence.count('FILEAPPEND')

    required_operations = ['FILECREATE', 'ETHEREUMTRANSACTION', 'FILEDELETE']

    if all(op in types_in_sequence for op in required_operations) and append_count >= 1:
        try:
            # check correct order of operations
            filecreate_index = types_in_sequence.index('FILECREATE')
            filedelete_index = types_in_sequence.index('FILEDELETE')
            ethereum_tx_indices = [idx for idx, t in enumerate(types_in_sequence) if t == 'ETHEREUMTRANSACTION']
            last_append_index = max(idx for idx, t in enumerate(types_in_sequence) if t == 'FILEAPPEND')

            if filecreate_index < last_append_index < min(ethereum_tx_indices) < filedelete_index:
                entity_ids = set(
                    tx['entity_id'] for tx in sequence if tx['type'] in ['FILECREATE', 'FILEAPPEND', 'FILEDELETE']
                )
                if len(entity_ids) == 1 and None not in entity_ids:
                    return True, append_count
                else:
                    return False, append_count
        except ValueError:
            return False, append_count

    return False, append_count

def calculate_and_print_statistics(total_eth_tx, big_tx_count, small_tx_count):
    """
    Calculates and prints statistics about transaction sizes.
    """
    if total_eth_tx == 0:
        print("\nStatistics:")
        print("No Ethereum transactions to analyze.")
        return

    percent_over = (big_tx_count / total_eth_tx) * 100
    percent_under = (small_tx_count / total_eth_tx) * 100

    print("\nStatistics:")
    print(f"Transactions over 5kb: {percent_over:.2f}%")
    print(f"Transactions under 5kb: {percent_under:.2f}%")

if __name__ == "__main__":
    # load from .env file
    load_dotenv()
    account_id = os.environ.get('ACCOUNT_ID')

    if not account_id:
        logging.error("Error: ACCOUNT_ID environment variable not set.")
        sys.exit(1)

    find_sequence_pattern(account_id)
