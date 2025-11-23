# ASA Stats Permission dApp

[![build-status](https://github.com/asastats/permission-dapp/actions/workflows/build.yml/badge.svg)](https://github.com/asastats/permission-dapp/actions/workflows/build.yml) [![docs](https://app.readthedocs.org/projects/permission-dapp/badge/?version=latest)](https://permission-dapp.readthedocs.io/en/latest/?badge=latest) [![codecov](https://codecov.io/gh/asastats/permission-dapp/graph/badge.svg?token=DQC4SRY8J9)](https://codecov.io/gh/asastats/permission-dapp)

The code in this repository is used to create and deploy the ASA Stats Permission dApp smart contract.

The repository also holds the scripts used to populate DAO governors Algorand boxes with the related votes and permissions, as well as for scheduled permission updates.


## Usage

The AlgoKit library requires at least *Python 3.12* to compile the smart contract.

Create and activate a Python virtual environment with:

```bash

python3 -m venv dapp
source dapp/bin/activate
```

Environment variables shouldn't reside in the repository, so the `.env` file has to be created based on `.env-example`:

```bash

cd dapp
cp .env.example .env
```

After you activate the Python environment and fill the .env file with the creator address mnemonic, you can compile the smart contract by issuing the following commands:

```bash

algokit compile py contract.py --out-dir artifacts
```

You can deploy and initially fund the newly created application on Testnet with:

```bash

python deploy.py
```


## Roadmap

