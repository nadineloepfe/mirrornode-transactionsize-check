import requests
import os
from dotenv import load_dotenv

def analyse_transactions(account_id):
    base_url = 'https://testnet.mirrornode.hedera.com'
    url = f'{base_url}/api/v1/transactions?account.id={account_id}&limit=500'

    all_transactions = []
    time_window = 30  # timewindow in seconds

    print(f'Fetching transactions for account: {account_id}')

    # fetch all tx by account
    while url:
        try:
            print(f'Fetching URL: {url}')
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
                'entity_id': tx.get('entity_id', None)
            })

            # pagination
            next_link = data['links'].get('next')
            url = f"{base_url}{next_link}" if next_link else None

        except requests.exceptions.RequestException as e:
            print(f"Error fetching transactions: {e}")
            break

    print(f'Total transactions fetched: {len(all_transactions)}')

    # process transactions
    total_ethereum_transactions, big_transactions, small_transaction_count = process_transactions(all_transactions, time_window)

    # output results
    big_transaction_count = sum(big_transactions.values())

    print(f'\nAnalysis for account {account_id}:')
    print(f'Total Ethereum transactions: {total_ethereum_transactions}')
    print(f'Ethereum transactions with file operations (big transactions): {big_transaction_count}')
    print(f'Ethereum transactions without file operations (small transactions): {small_transaction_count}')

    print('\nBig Transaction Sequences Breakdown:')
    sorted_chunks = sorted(big_transactions.items(), key=lambda x: int(x[0].split(' ')[0]) if x[0][0].isdigit() else 11)
    for chunk_key, count in sorted_chunks:
        print(f'{chunk_key}: {count}')


def process_transactions(all_transactions, time_window=30):
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
            sequence, indices = collect_sequence(i, all_transactions, time_window)
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
                        print("\nFirst big transaction sequence found (for sanity check):")
                        for seq_tx in sequence:
                            print(f"Timestamp: {seq_tx['timestamp']}, Type: {seq_tx['type']}, Entity ID: {seq_tx.get('entity_id')}")
                        first_sequence_printed = True


    # process remaining ethereum transactions not part of big transactions
    for i, tx in enumerate(all_transactions):
        if i not in processed_indices and tx['type'] == 'ETHEREUMTRANSACTION':
            # add if transaction wasn't already processed as part of a big transaction
            total_ethereum_transactions += 1
            small_transaction_count += 1
            processed_indices.add(i)

    return total_ethereum_transactions, big_transactions, small_transaction_count


def collect_sequence(start_index, all_transactions, time_window):
    """
    Collects a sequence of transactions within the given time window starting from a FILECREATE.
    """
    sequence = []
    indices = []
    n = len(all_transactions)
    create_time = all_transactions[start_index]['timestamp']
    file_entity_id = all_transactions[start_index]['entity_id']

    append_count = 0
    has_ethereum_tx = False

    for i in range(start_index, n):
        tx = all_transactions[i]
        time_diff = tx['timestamp'] - create_time

        if time_diff > time_window:
            # timewindow exceeded
            break

        # check file operations have the same entity_id
        if tx['type'] in ['FILEAPPEND', 'FILEDELETE']:
            if tx['entity_id'] != file_entity_id:
                continue  

        sequence.append(tx)
        indices.append(i)

        if tx['type'] == 'FILEAPPEND':
            append_count += 1
        elif tx['type'] == 'ETHEREUMTRANSACTION':
            has_ethereum_tx = True
        elif tx['type'] == 'FILEDELETE':
            break

    return sequence, indices


def is_valid_big_transaction(sequence):
    """
    Checks if a given sequence is a valid big transaction (has FILECREATE, FILEAPPEND, ETHEREUMTRANSACTION, FILEDELETE).
    """
    types_in_sequence = [tx['type'] for tx in sequence]
    append_count = types_in_sequence.count('FILEAPPEND')

    if 'FILECREATE' in types_in_sequence and \
            append_count >= 1 and \
            'ETHEREUMTRANSACTION' in types_in_sequence and \
            'FILEDELETE' in types_in_sequence:

        # check correct order of operations: FILECREATE -> FILEAPPEND -> ETHEREUMTRANSACTION -> FILEDELETE
        filecreate_index = types_in_sequence.index('FILECREATE')
        filedelete_index = types_in_sequence.index('FILEDELETE')
        ethereum_tx_indices = [idx for idx, t in enumerate(types_in_sequence) if t == 'ETHEREUMTRANSACTION']
        last_append_index = max(idx for idx, t in enumerate(types_in_sequence) if t == 'FILEAPPEND')

        if filecreate_index < last_append_index < min(ethereum_tx_indices) < filedelete_index:
            entity_ids = set(tx['entity_id'] for tx in sequence if tx['type'] in ['FILECREATE', 'FILEAPPEND', 'FILEDELETE'])
            if len(entity_ids) == 1:
                return True, append_count
            else:
                return False, append_count

    return False, append_count


if __name__ == "__main__":
    # load from .env file
    load_dotenv()
    account_id = os.environ.get('ACCOUNT_ID')

    if not account_id:
        print("Error: ACCOUNT_ID environment variable not set.")
        sys.exit(1)

    analyse_transactions(account_id)