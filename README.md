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

> **Last Updated:** November 2025
> **Status:** On Track

### Overview
The Permission dApp foundation traces its origins to the establishment of the ASA Stats DAO, evolving through DAO governance seat updates, two years of governance staking programs, deployment of subscription dApps on Subtopia.io, and culminating with the deployment of the first iteration of the Permission dApp on Mainnet.

---

### Timeline Legend
- **Completed** - Milestone achieved
- **In Progress** - Currently in development
- **Planned** - Scheduled for future development
- **Future** - Under consideration

---

### Historical Milestones

#### Q4 2021 - Completed
- **[Open letter to the ASA Stats governors](https://github.com/asastats/dao-discussion/discussions/1)** - Announcing the establishment of ASA Stats DAO
- **[Governor Seats Update 2021-12-12](https://github.com/asastats/dao-discussion/discussions/6)** - Governance composition update

#### Q1 2022 - Completed
- **[Governor Seats Update 2022-03-30](https://github.com/asastats/dao-discussion/discussions/9)** - Governance composition update

#### Q2 2022 - Completed
- **[Governor Seats Update 2022-06-20](https://github.com/asastats/dao-discussion/discussions/12)** - Governance composition update
- **[Voting dApp introductory technical discussion](https://github.com/asastats/dao-discussion/discussions/10)** - Initial technical planning

#### Q3 2022 - Completed
- **[Governor Seats Update 2022-09-23](https://github.com/asastats/dao-discussion/discussions/13)** - Governance composition update

#### Q4 2022 - Completed
- **[Governor Seats Update 2022-12-24](https://github.com/asastats/dao-discussion/discussions/14)** - Governance composition update

---

### Recent Development Cycle

#### Q1 2023 - Completed
- **[ASA Stats DAO governance staking on GARD platform](https://github.com/asastats/dao-discussion/discussions/15)** - First official staking program
- **[Governor Seats Update 2023-03-31](https://github.com/asastats/dao-discussion/discussions/16)** - Governance composition update

#### Q3 2023 - Completed
- **[Governor Seats Update 2023-07-28](https://github.com/asastats/dao-discussion/discussions/17)** - Governance composition update
- **[Governance staking program migrated to Cometa](https://medium.com/@asastats/asa-stats-governance-staking-program-migrates-to-cometa-b69c3a316349)** - Platform transition

#### Q1 2024 - Completed
- **[The second year of the official Governance staking program started](https://medium.com/@asastats/dao-subscription-and-governance-staking-updates-c2d3244f4c03)** - Program continuation and enhancements

#### Q3 2024 - Completed
- **[Governor Seats Update 2024-09-06](https://github.com/asastats/dao-discussion/discussions/18)** - Governance composition update
- **[The final iteration of the Governance staking program started](https://medium.com/@asastats/the-final-iteration-of-our-governance-staking-pool-begins-this-week-f41287a040cc)** - Concluding staking phase

#### Q4 2024 - Completed
- **[Preliminary results for the first year of the Governance staking programs announced](https://github.com/asastats/channel/discussions/1128)** - Staking program outcomes
- **[Data collecting and processing development; development of the Permission dApp using PyTeal v0.27](https://lora.algokit.io/testnet/application/732206032)** - Technical development on Testnet

#### Q1 2025 - Completed
- **[Deployment of the ASA Stats subscription dApps on subtopia.io](https://medium.com/@asastats/asa-stats-launches-user-system-and-subscription-service-d99aed6ad98e)** - Subscription service launch
- **[Initial deployment of the Permission dApp on the Algorand Mainnet](https://allo.info/tx/VXRJLIJRZDKHMZYSSX5IV4X4OGLJ4BHP37T52Y7IQNDWEAT5ECOA)** - Mainnet deployment
- **[ASA Stats launched user system and subscription service](https://medium.com/@asastats/asa-stats-launches-user-system-and-subscription-service-d99aed6ad98e)** - User system implementation

#### Q2 2025 - Completed
- **[Preliminary results of the Governance staking programs announced](https://github.com/asastats/channel/discussions/1277)** - Final staking outcomes

#### Q3 2025 - Completed
- **[Governor Seats Update 2025-08-08](https://github.com/asastats/dao-discussion/discussions/19)** - Latest governance composition update
- **[Permission dApp xGov proposal submitted](https://forum.algorand.co/t/xgov-3240198097-asa-stats-permission-dapp/14959)** - Funding proposal submission
- **[The Permission dApp xGov proposal was rejected in the xGov voting because the xGov Quorum wasn't reached](https://xgov.algorand.co/proposal/3240198097)** - Proposal outcome
- **[Permission dApp is recreated using Algorand Python (puyapy v5.4.0)](https://xgov.algorand.co/proposal/3240198097)** - Technical improvements
- **[Unit tests for the newly recreated smart contract use Algorand Python Testing v1.1.0](https://github.com/asastats/permission-dapp/blob/main/dapp/tests/test_contract.py)** - Enhanced testing
- **[Integration tests for Localnet using AlgoKit utils v4.2.2](https://github.com/asastats/permission-dapp/blob/main/dapp/tests/test_contract.py)** - Comprehensive testing suite

---

### Current Development (Q4 2025)

#### Q4 2025 - In Progress
> It was clear from the Algorand Foundation and xGov Committee officials' statements that the first proposal was rejected in the official voting as [*a victim of being first*](https://forum.algorand.co/t/xgov-pause-for-parameters-change/15053/3?u=ipaleka) and [*as this was the first iteration with clear participation quorum kinks*](https://forum.algorand.co/t/xgov-pause-for-parameters-change/15053/5?u=ipaleka).

- **Resubmitting improved xGov proposal** - Focus on smart contract and code improvements
- **Expected submission**: December 2025

---

### Future Vision (2026)

#### Q2 2026 - Planned
- **Intensive discussion about the implementation of the ASA Stats DAO voting dApp** - Planning phase for voting system

#### Q3 2026 - Planned
- **Develop permission dApp update** based on the needs of the Voting dApp provider/developer(s)
- **Publish new Governor Seats Update** and update Permission dApp repository with new governor seats' values

#### Q4 2026 - Planned
- **Publish the updated Permission dApp on Mainnet** - Full deployment of enhanced system

---

### Development Progress

| Phase | Status | Key Milestones |
|-------|--------|----------------|
| Continuous Governance | Ongoing | Regular governance composition updates (2021-present) |
| Staking Programs | Complete | Multi-platform implementation (2023-2024) |
| Permission dApp | In Progress | Mainnet deployment, ongoing development (2025-2026) |
| xGov Funding | In Progress | Proposal resubmission with improvements (2025) |
| Future Ecosystem | Planned | Voting dApp integration (2026) |

---

### Related Resources

- [ASA Stats DAO Discussions](https://github.com/asastats/dao-discussion)
- [Permission dApp Repository](https://github.com/asastats/permission-dapp)
- [ASA Stats Channel](https://github.com/asastats/channel)
- [Algorand xGov Platform](https://xgov.algorand.co/)

---

### Community Engagement
We welcome community input on our development roadmap. Please participate in our discussions and help shape the future of ASA Stats DAO.