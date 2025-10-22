
[![build-status](https://github.com/asastats/permission-dapp/actions/workflows/test.yml/badge.svg)](https://github.com/asastats/permission-dapp/actions/workflows/test.yml) [![docs](https://app.readthedocs.org/projects/permission-dapp/badge/?version=latest)](https://permission-dapp.readthedocs.io/en/latest/?badge=latest)

# ASA Stats Permission dApp

The code in this repository is used to create and deploy the ASA Stats Permission dApp smart contract to the Algorand blockchain (Mainnet and/or Testnet).

The repository also holds the scripts used to populate related Algorand boxes with the votes and permissions for the ASA Stats DAO governors and subscribers, as well as for scheduled permission updates.

The Permission dApp (that is deployed on Mainnet - https://allo.info/application/2685515413) is responsible for managing access permissions and tracking governance votes. It functions as the central authority for feature authorization for ASA Stats subscribers and DAO Governors, while also providing the foundational framework for all future DAO voting activities.  
  
## Why It's Useful  
  
While ASA Stats uses this dApp to track DAO governor votes and permissions, the repository can be adapted by any organization seeking to manage measurable internal statuses. We are happy to assist others in adjusting the code for their specific use cases.  
  
We've also made sure the project is robust and easy to work with:  
  
- Comprehensive Testing: Everything is covered by unit tests, and we run extra security-focused tests on Algorand Testnet.  
  
- Continuous Integration: We use GitHub Actions to automatically test every single commit against three different Python versions (https://github.com/asastats/permission-dapp/action).  
  
- Full Documentation: The code is well-documented, and we automatically build and publish the docs to Read The Docs with every update (https://permission-dapp.readthedocs.io/en/latest/)
