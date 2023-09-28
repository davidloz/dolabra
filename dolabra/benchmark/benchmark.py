import csv
import json
import hashlib
import logging
import os
import random
import time
import pprint
import glob

from functools import lru_cache
from typing import Optional, Set, Text, Tuple

from mythril.support.signatures import SignatureDB
from mythril.mythril import MythrilDisassembler

from dolabra.benchmark import benchmark_state_path
from dolabra.benchmark.verification_db import Contract, Flag
from dolabra.benchmark.contract_repository import ContractRepository
from dolabra.benchmark.function_repository import FunctionRepository
from dolabra.benchmark.flagged_function_repository import FlaggedFunctionRepository

from dolabra.analysis.module.modules.loader import ModuleLoader
from dolabra.analysis.symbolic import SymbolicWrapper
from dolabra.analysis.module.modules.loader import MODULES
from dolabra.contract_loaders.loader import LoaderType, Loader

TIME_FORMAT = '%Y-%m-%d %H:%M:%S (%z)'

log = logging.getLogger(__name__)
contract_repository = ContractRepository()
function_repository = FunctionRepository()
flagged_function_repository = FlaggedFunctionRepository()
signature_db = SignatureDB(enable_online_lookup=True)

def get_binary_answer(allow_unknown=False) -> Optional[bool]:
    valid_answers = f"[y/n{'/u' if allow_unknown else ''}]"
    answer = input(f"> Your answer {valid_answers}: ")
    while answer not in {'y', 'n'} | ({'u'} if allow_unknown else set()):
        answer = input(f"> Enter a valid answer {valid_answers}: ")
    if answer == 'y':
        return True
    elif answer == 'n':
        return False
    else:
        return None


def generate_contract_sample(instance_count: int,
                             sample_size: int,                             
                             ) -> Set[int]:    
    
    return set(random.sample(range(0, instance_count), sample_size))

def count_files_in_directory(directory):
    return len([name for name in os.listdir(directory) if os.path.isfile(os.path.join(directory, name))])

def new_benchmark(args) -> None:
    random.seed(args.random_seed)
    #instance_count = count_rows(args.filename, delimiter=args.csv_delimiter) - 1 if args.has_header else 0
    instance_count = count_files_in_directory(args.dirpath)
    print("instance", instance_count)
    #file_sha256sum = hashlib.sha256(open(args.filename, 'rb').read()).hexdigest()
    contract_sample = generate_contract_sample(instance_count, args.sample_size)
    '''
    benchmark_report = Report(args.strategy.capitalize(), args.random_seed, args.timeout, args.max_depth, args.verification_ratio,
                              contracts_filename=os.path.basename(args.filename), file_sha256sum=file_sha256sum,
                              start_time=time.strftime(TIME_FORMAT), target_version=args.compiler_target.raw if args.compiler_target else None)
    
    '''
    strategy_name = args.strategy.replace('-', '_').upper()
    strategy_loader = ModuleLoader()
    strategy_loader.set_modules([MODULES[strategy_name]()])
    positive_instances = set()
    files = glob.glob(os.path.join(args.dirpath, "*.hex"))
    #print(files)

    # Generate the contract sample indexes
    sampled_indexes = generate_contract_sample(instance_count, args.sample_size)

    # Extract the files with the sampled indexes along with their original indexes
    sampled_files = [(index, file) for index, file in enumerate(files) if index in sampled_indexes]

    #print(sampled_indexes, sampled_files)

    for i, file_name in sampled_files:        
        #with open(args.filename, 'r') as csv_file:
        #with open(file_name, 'r') as file:
        print("file_name", file_name)
        base_file_name = os.path.basename(file_name)
        # Remove the file extension
        base_file_name_without_extension = os.path.splitext(base_file_name)[0]
        block_id, target_address = base_file_name_without_extension.split('-')
        #print("file content", file.read())
        
    
        log.info('Analyzing contract %d/%d at address %s', i + 1, instance_count, target_address)
        #print("pattth", (args.dirpath + '/' + base_file_name))
        contract_loader = Loader.get_contract(LoaderType.BINARY, path=file_name)
        #print(contract_loader)
        #loader_factory = get_factory(LoaderFactoryType.JSON_RPC, address=target_address, rpc=rpc)
        #contract_loader = loader_factory.create()
        symbolic_analysis = SymbolicWrapper(contract_loader)    
        report = symbolic_analysis.run_analysis()
        pprint.pprint(report, width=1)
        #analysis_report = SymbolicWrapper().execute(contract_loader=contract_loader, timeout=args.timeout, max_depth=args.max_depth)
        
        if sum(len(report_item) for report_item in report) > 0:
            positive_instances.add(i)
        else:
            log.info('Nothing found for contract %d/%d at address %s', i + 1, instance_count, target_address)
        
        '''
        detected_functions = [result.__dir__
                            for report_item in report if len(report_item) > 0
                            for result in report_item]
        '''
        
        #compiler_version = row[args.version_column] if args.version_column is not None else None
        function_hashes = contract_loader.disassembly().func_hashes if contract_loader.disassembly() else []

        #print(detected_functions)
        #benchmark_report.add_result(Result(function_hashes, target_address, i, detected_functions, compiler_version=compiler_version))
        strategy_loader.reset_modules()
    #benchmark_report.end_time = time.strftime(TIME_FORMAT)
    negative_instances = sampled_indexes - positive_instances
    positive_sample = set(random.sample(positive_instances, round(len(positive_instances) * args.verification_ratio)))
    negative_sample = set(random.sample(negative_instances, round(len(negative_instances) * args.verification_ratio)))
    print("Positive sample", positive_sample)
    print("sampled indexes, positive instances, Negative instances", sampled_indexes, positive_instances, negative_instances)
    #save_benchmark_state(benchmark_report, positive_sample, negative_sample)
    if args.interactive:
        #start_verification(benchmark_report, positive_sample | negative_sample)
        os.remove(benchmark_state_path)


'''
def verify_benchmark(benchmark_state_file: Text) -> None:
    report, positive_sample, negative_sample = load_benchmark_state(benchmark_state_file)
    start_verification(report, positive_sample | negative_sample)
    os.remove(benchmark_state_file)
    '''


def benchmark(args) -> None:
    if args.benchmark_command == 'new':
        if os.path.exists(benchmark_state_path):
            print('! A benchmark state from a previous session exists. Do you want to override it?')
            answer = get_binary_answer()
            if not answer:
                print('! Terminating. Run \'ithil benchmark verify\' to manually verify the old benchmark state.')
                return
        new_benchmark(args)
    '''
    elif args.benchmark_command == 'verify':
        verify_benchmark(args.benchmark_state_file)
    '''
