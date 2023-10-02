import logging
import os
import random
import pprint
import glob

from typing import Optional, Set

from dolabra.benchmark import benchmark_state_path

from dolabra.analysis.module.modules.loader import ModuleLoader
from dolabra.analysis.symbolic import SymbolicWrapper
from dolabra.analysis.module.modules.loader import MODULES
from dolabra.contract_loaders.loader import LoaderType, Loader

TIME_FORMAT = '%Y-%m-%d %H:%M:%S (%z)'

log = logging.getLogger(__name__)

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
    instance_count = count_files_in_directory(args.dirpath)
    print("instance", instance_count)
    
    strategy_name = args.strategy.replace('-', '_').upper()
    strategy_loader = ModuleLoader()
    strategy_loader.set_modules([MODULES[strategy_name]()])
    positive_instances = set()
    files = glob.glob(os.path.join(args.dirpath, "*.hex"))

    # Generate the contract sample indexes
    sampled_indexes = generate_contract_sample(instance_count, args.sample_size)

    # Extract the files with the sampled indexes along with their original indexes
    sampled_files = [(index, file) for index, file in enumerate(files) if index in sampled_indexes]


    for i, file_name in sampled_files:        
        base_file_name = os.path.basename(file_name)
        # Remove the file extension
        base_file_name_without_extension = os.path.splitext(base_file_name)[0]
        block_id, target_address = base_file_name_without_extension.split('-')
    
        log.info('Analyzing contract %d/%d at address %s', i + 1, instance_count, target_address)
        contract_loader = Loader.get_contract(LoaderType.BINARY, path=file_name)

        symbolic_analysis = SymbolicWrapper(contract_loader)    
        report = symbolic_analysis.run_analysis()
        pprint.pprint(report, width=1)
        
        if sum(len(report_item) for report_item in report) > 0:
            positive_instances.add(i)
        else:
            log.info('Nothing found for contract %d/%d at address %s', i + 1, instance_count, target_address)
        

        strategy_loader.reset_modules()
    negative_instances = sampled_indexes - positive_instances
    positive_sample = set(random.sample(positive_instances, round(len(positive_instances) * args.verification_ratio)))
    print("Positive sample", positive_sample)
    print("sampled indexes, positive instances, Negative instances", sampled_indexes, positive_instances, negative_instances)
    if args.interactive:
        os.remove(benchmark_state_path)

def benchmark(args) -> None:
    if args.benchmark_command == 'new':
        if os.path.exists(benchmark_state_path):
            print('! A benchmark state from a previous session exists. Do you want to override it?')
            answer = get_binary_answer()
            if not answer:
                print('! Terminating.')
                return
        new_benchmark(args)
