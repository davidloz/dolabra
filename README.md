## dolabra

Dolabra is a semantic analysis tool for EVM bytecode based on [Mythril](https://github.com/ConsenSys/mythril) and [Ithildin](https://github.com/metagon/ithildin). By using symbolic execution and taint analysis, it aims at detecting functions that are instances of given patterns. It is primarily written in Python and contains several modules and loaders to facilitate the analysis of Solidity contracts.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Modules](#modules)
- [Contract Loaders](#contract-loaders)

## Features
- Analysis of Solidity contracts.
- Symbolic analysis of contracts.
- Multiple contract loaders to load contracts from different sources.
- Modular architecture to facilitate the addition of new analysis modules.
- CLI for easy interaction.

## Installation
Clone the repository and install the required dependencies.
```sh
$ pip install dolabra
```

## Usage
Dolabra can analyze contracts provided in one of the following formats. Run dolabra --help to see all arguments that the program accepts.

### Deployed contracts using RPC
The following command analyzes the contract bytecode at the given target address. You'll have to supply the RPC endpoint using the `--rpc` argument, unless you are using geth, in which case the default endpoint `http://localhost:8545` is used.
```sh
$ dolabra analyze --address 0x45e650d1AcE4d63541b80793510D585AceA9C37B
```

### Specify solc compiler
This command will use the solc compiler that is currently installed on your system if --solc is not specified. Older compilers can be downloaded from the [ethereum/solc-bin](https://github.com/ethereum/solc-bin) repository (make sure you make them executable).
```sh
$ dolabra analyze --sol test.sol --solc ./solc-linux-amd64-v0.8.4+commit.c7e474f2
```

### Creation Bytecode
Provide a file containing the EVM (creation) bytecode in one line.

```sh
$ dolabra analyze --bin ./creation_bytecode_example.bin
```

### Runtime Bytecode
Provide a file containing the runtime bytecode in one line.

```sh
$ dolabra analyze --bin-runtime ./runtime_bytecode_example.bin
```

## Modules
Dolabra contains several analysis modules located in the `dolabra/analysis/module/modules` directory. Each module is designed to perform a specific type of analysis on Solidity contracts. The available modules are:
- `Getter`: Analyzes getter functions in contracts.
- `Payable`: Analyzes payable functions in contracts, needs a more abstract approach.
- `Setter`: Analyzes setter functions in contracts.
- `StorageCallerCheck`: Checks storage caller in contracts.

The followings serve as a basis for the modules (providing extendability):

- `BaseModule`: The base module from which other modules are derived.
- `Loader`: Loads contracts for analysis.
- `Taints`: Taint classes for taint analysis.
- `Utils`: Provides utility functions for modules.

## Contract Loaders
Dolabra provides several contract loaders located in the `dolabra/contract_loaders` directory to load contracts from different sources such as files, JSON-RPC, and Solidity sources. The available contract loaders are:
- `BinaryLoader`: Loads binary contracts.
- `ContractLoader`: The base loader from which other loaders are derived.
- `FileLoader`: Loads contracts from files.
- `JsonrpcLoader`: Loads contracts using JSON-RPC.
- `Loader`: Provides a generic loader interface.
- `SolidityLoader`: Loads Solidity contracts.

## Pitfalls
- cargo/rust should be installed because of mythril
- There is currently a known incompatibility between rust and blake2b-py [GitHub Issue](https://github.com/Consensys/mythril/issues/1666), using a nightly build of rust resolved it.

## Development Setup

Install all the requirements inside a virtual environment or globally. For development and testing purposes, there is the possibility to whitelist modules in [symbolic.py](https://github.com/davidloz/dolabra/blob/dev/dolabra/analysis/symbolic.py#L33)

### Installing Dolabra Inside a Virtual Environment (Recommended)

```bash
$ cd <dolabra-root>
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip3 install -e .
```

### Installing Dolabra Globally

```bash
$ $ pip install dolabra
```
