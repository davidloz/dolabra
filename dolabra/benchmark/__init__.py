import os

dolabra_dir_name = '.dolabra'
dolabra_home = os.path.join(os.path.expanduser('~'), dolabra_dir_name)

verifications_db_file = 'verifications.db'
verifications_db_path = os.path.join(dolabra_home, verifications_db_file)

benchmark_state_file = 'benchmark_state.json'
benchmark_state_path = os.path.join(dolabra_home, benchmark_state_file)

# Create .dolabra home directory if it doesn't exist
if not os.path.exists(dolabra_home):
    os.mkdir(dolabra_home)

