from argparse import ArgumentParser
from typing import Text
import pprint

import mythril.support.support_args

from dolabra.analysis.symbolic import SymbolicWrapper
from dolabra.contract_loaders.loader import LoaderType, Loader

from dolabra.benchmark.benchmark import benchmark

from dolabra.analysis.module.modules.loader import MODULES
from dolabra.benchmark import benchmark_state_path

# Default analysis arguments
DEFAULT_MAX_DEPTH = 128
DEFAULT_RPC = 'http://127.0.0.1:8545'
DEFAULT_SOLC = 'solc'
DEFAULT_TIMEOUT_ANALYSIS = 240

# Default benchmark arguments
DEFAULT_DELIMITER = ','
DEFAULT_HAS_HEADER = True
DEFAULT_ADDRESS_COLUMN = 0
DEFAULT_SAMPLE_SIZE = 15
DEFAULT_TIMEOUT_BENCHMARK = 90
DEFAULT_SEED = 1
DEFAULT_VERIFICATION_RATIO = 0.1

def init_parser() -> ArgumentParser:
    parser = ArgumentParser(description="Dolabra - an Ethereum Smart Contract Analyzer")
    #parser.add_argument("contract_address", help="The contract address to analyze")
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    # Add analysis parser
    analysis_parser = subparsers.add_parser('analyze', help='begin analysis of a contract')
    init_analysis_parser(analysis_parser)
    # Add benchmark parser
    benchmark_parser = subparsers.add_parser('benchmark', help='execute benchmarking tool')
    init_benchmark_parser(benchmark_parser)

    return parser

def init_analysis_parser(parser: ArgumentParser) -> None:

    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('-a', '--address', metavar='ADDRESS', type=Text, help='contract address to analyze')
    input_group.add_argument('-s', '--sol', metavar='PATH', type=Text, dest='sol_path', help='path to solidity contract')
    input_group.add_argument('-b', '--bin', metavar='PATH', type=Text, dest='bin_path',
                             help='path to file containing contract creation bytecode')
    input_group.add_argument('-r', '--bin-runtime', metavar='PATH', type=Text, dest='runtime_path',
                             help='path to file containing runtime bytecode')

    sym_exec_arguments = parser.add_argument_group('symbolic execution arguments')
    sym_exec_arguments.add_argument('--timeout', metavar='SEC', type=int, default=DEFAULT_TIMEOUT_ANALYSIS,
                                    help='symbolic execution timeout (default: {})'.format(DEFAULT_TIMEOUT_ANALYSIS))
    sym_exec_arguments.add_argument('--max-depth', metavar='DEPTH', type=int, default=DEFAULT_MAX_DEPTH,
                                    help='max graph depth (default: {})'.format(DEFAULT_MAX_DEPTH))

    networking_group = parser.add_argument_group('networking arguments')
    networking_group.add_argument('--rpc', metavar="RPC", type=Text, default=DEFAULT_RPC,
                                  help='JSON RPC provider URL (default: \'{}\')'.format(DEFAULT_RPC))

    compilation_group = parser.add_argument_group('compilation arguments')
    compilation_group.add_argument('--solc', metavar='SOLC', type=Text, default=DEFAULT_SOLC,
                                   help='solc binary path (default: \'{}\')'.format(DEFAULT_SOLC))
    
def init_benchmark_parser(parser: ArgumentParser) -> None:
    benchmark_subparsers = parser.add_subparsers(dest='benchmark_command', help='Commands')

    new_benchmark_parser = benchmark_subparsers.add_parser('new', help='start a new benchmark')
    #new_benchmark_parser.add_argument('filename', metavar='FILE', type=str, help='the csv file containing contract instances')
    new_benchmark_parser.add_argument('--dirpath', metavar='FILE', type=str, help='the directory containing the deployment codes of the contracts')
    strategies_options = [strategy.replace('_', '-').lower() for strategy in MODULES.keys()]
    new_benchmark_parser.add_argument('--strategy', choices=strategies_options, required=True, help='the strategy to benchmark')
    new_benchmark_parser.add_argument('--interactive', action='store_true', help='after analysis proceed to interactive verification mode')
    
    new_benchmark_parser.add_argument('--timeout', metavar='SEC', type=int, default=DEFAULT_TIMEOUT_BENCHMARK,
                                      help='the execution timeout for each contract (default: {})'.format(DEFAULT_TIMEOUT_BENCHMARK))
    new_benchmark_parser.add_argument('--max-depth', metavar='DEPTH', type=int, default=DEFAULT_MAX_DEPTH,
                                      help='max graph depth (default: {})'.format(DEFAULT_MAX_DEPTH))

    sampling_group = new_benchmark_parser.add_argument_group('sampling options')
    sampling_group.add_argument('--sample-size', metavar='SIZE', type=int, default=DEFAULT_SAMPLE_SIZE,
                                help='the sample size to be picked from the CSV instances (default: {})'.format(DEFAULT_SAMPLE_SIZE))
    sampling_group.add_argument('--random-seed', metavar='SEED', type=int, default=DEFAULT_SEED,
                                help='a seed for the sampling RNG (default: {})'.format(DEFAULT_SEED))
    sampling_group.add_argument('--verification-ratio', metavar='RATIO', type=float, default=DEFAULT_VERIFICATION_RATIO,
                                help='the ratio of the sampled contracts to manually verify (default: {})'.format(DEFAULT_VERIFICATION_RATIO))

    '''
    csv_group = new_benchmark_parser.add_argument_group('CSV arguments')
    csv_group.add_argument('--has-header', action='store_true', default=DEFAULT_HAS_HEADER,
                           help='does the CSV file contain a header (default: {})'.format(DEFAULT_HAS_HEADER))
    csv_group.add_argument('--csv-delimiter', metavar='DELIMITER', type=str, default=DEFAULT_DELIMITER,
                           help='the CSV delimiter (default: \'{}\')'.format(DEFAULT_DELIMITER))
    csv_group.add_argument('--address-column', metavar='COL', type=int, default=DEFAULT_ADDRESS_COLUMN,
                           help='column index that contains the contract addresses (default: {})'.format(DEFAULT_ADDRESS_COLUMN))
    csv_group.add_argument('--compiler-column', metavar='COL', type=int, help='the column containing the compiler name')
    csv_group.add_argument('--version-column', metavar='COL', type=int,
                           help='column index that contains the compiler version used')
    '''

    verify_benchmark_parser = benchmark_subparsers.add_parser('verify', help='verify previously stored benchmark state in interactive mode')
    verify_benchmark_parser.add_argument('--file', metavar='FILE', dest='benchmark_state_file', default=benchmark_state_path,
                                         help='path to benchmark state file (default: {})'.format(benchmark_state_path))    



def init_mythril(args):
    mythril.support.support_args.args.pruning_factor = 0

    

def analyze(args) -> None:
    # Get the contract loader factory based on the specified options
    if args.bin_path:
        contract_loader = Loader.get_contract(LoaderType.BINARY, path=args.bin_path)
    elif args.runtime_path:
        contract_loader = Loader.get_contract(LoaderType.RUNTIME, path=args.runtime_path)
    elif args.sol_path:
        contract_loader = Loader.get_contract(LoaderType.SOLIDITY, path=args.sol_path, solc=args.solc)
    elif args.address:
        contract_loader = Loader.get_contract(LoaderType.JSON_RPC, address=args.address, rpc=args.rpc)
    else:
        raise NotImplementedError('This feature is not available')

    symbolic_analysis = SymbolicWrapper(contract_loader)
    
    report = symbolic_analysis.run_analysis()
    pprint.pprint(report, width=1)

def main():
    parser = init_parser()
    args = parser.parse_args()

    init_mythril(args)
    
    if args.command == 'analyze':
        analyze(args)
    elif args.command == 'benchmark' and args.benchmark_command is not None:
        benchmark(args)
    else:
        parser.print_help()
        exit(1)

if __name__ == "__main__":
    main()
