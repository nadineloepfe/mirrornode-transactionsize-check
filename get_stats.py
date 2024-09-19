import subprocess
import re

def run_script(script_name):
    """
    Runs the specified Python script and captures its output.
    """
    result = subprocess.run(['python', script_name], capture_output=True, text=True)
    return result.stdout

def extract_transaction_stats(output, script_name):
    """
    Extracts the statistics of transactions over and under 5kb from the script's output.
    """
    over_5kb = 0
    under_5kb = 0
    total_tx = 0

    if script_name == 'find_sequence_pattern.py':
        match = re.search(r"Total Ethereum transactions: (\d+)", output)
        if match:
            total_tx = int(match.group(1))
        match = re.search(r"Ethereum transactions with file operations \(big transactions\): (\d+)", output)
        if match:
            over_5kb = int(match.group(1))
        under_5kb = total_tx - over_5kb

    elif script_name == 'check_function_param_size.py':
        match = re.search(r"Total CONTRACTCALL and CONTRACTCREATEINSTANCE transactions fetched: (\d+)", output)
        if match:
            total_tx = int(match.group(1))
        match = re.search(r"Transactions over 5kb \(function_parameters > 5kb\): (\d+)", output)
        if match:
            over_5kb = int(match.group(1))
        match = re.search(r"Transactions under 5kb \(function_parameters <= 5kb\): (\d+)", output)
        if match:
            under_5kb = int(match.group(1))

    return total_tx, over_5kb, under_5kb

def calculate_percentage(over_5kb, under_5kb):
    """
    Calculates the percentage of transactions over and under 5kb.
    """
    total = over_5kb + under_5kb
    if total == 0:
        return 0, 0
    over_5kb_percent = (over_5kb / total) * 100
    under_5kb_percent = (under_5kb / total) * 100
    return over_5kb_percent, under_5kb_percent

if __name__ == "__main__":
    # run check_function_param_size.py
    print("\nRunning check_function_param_size.py...")
    contract_output = run_script('contract_endpoint/check_function_param_size.py')

    # run find_sequence_pattern.py
    print("\nRunning find_sequence_pattern.py...")
    transaction_output = run_script('transaction_endpoint/find_sequence_pattern.py')

    # extract stats for contract and transaction endpoints
    total_contract, contract_over_5kb, contract_under_5kb = extract_transaction_stats(contract_output, 'check_function_param_size.py')
    total_tx, tx_over_5kb, tx_under_5kb = extract_transaction_stats(transaction_output, 'find_sequence_pattern.py')

    # calculate percentages
    contract_over_5kb_percent, contract_under_5kb_percent = calculate_percentage(contract_over_5kb, contract_under_5kb)
    tx_over_5kb_percent, tx_under_5kb_percent = calculate_percentage(tx_over_5kb, tx_under_5kb)

    print("\nOutput of find_sequence_pattern.py:\n")
    print(transaction_output)

    print("\nOutput of check_function_param_size.py:\n")
    print(contract_output)

    # display the statistics
    print("---------------------------------------")
    print(             "Statictics")
    print("---------------------------------------")
    print("\n>5kb Transactions:")
    print(f"Ethereum Transactions -> /transactions endpoint: {tx_over_5kb_percent:.2f}%")
    print(f"Contract Transactions -> /contract endpoint: {contract_over_5kb_percent:.2f}%")

    print("\n<5kb Transactions:")
    print(f"Ethereum Transactions -> /transactions endpoint: {tx_under_5kb_percent:.2f}%")
    print(f"Contract Transactions -> /contract endpoint: {contract_under_5kb_percent:.2f}%")
