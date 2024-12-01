About
=====

This repository contains code for the
`ASA Stats Permission dApp <https://medium.com/@asastats/asa-stats-launches-user-system-and-subscription-service-d99aed6ad98e>`_,
which is deployed on the
`Algorand Mainnet <https://allo.info/application/2685515413>`_.

Besides the smart code itself found in the `artifacts` directory, this repository in the `DAO` directory 
contains governance seat votes data of all the 
`selected ASA Stats DAO governors <https://github.com/asastats/dao-discussion/discussions>`_,
as well as scripts for initial and scheduled updates of the Permission dApp users’ boxes.


Structure
---------

.. code-block:: bash

    dapp/
    ├── artifacts/
    ├── DAO/
    ├── tests/
    ├── config.py
    ├── contract.py
    ├── deploy.py
    ├── foundation.py
    ├── helpers.py
    ├── network.py
    └── utils.py


Smart contract
^^^^^^^^^^^^^^

Module `contract` contains Permission dApp's
`PyTeal <https://github.com/algorand/pyteal>`_ application code.
After that code is run (by invoking `python contract.py` inside the created Python environment),
the smart contract is converted to
`TEAL <https://dev.algorand.co/concepts/smart-contracts/languages/teal/>`_
and placed inside the `artifacts` directory.

The actual deployment of the smart contract to the Algorand Mainnet is done by running `python deploy.py`.


Update data
^^^^^^^^^^^

The initial creation of Algorand boxes for the ASA Stats DAO governors is done by running
`python foundation.py`. That process fills the boxes with the governors' seat votes
(and calculated permissions) loaded from the JSON files found in the `DAO` directory.

For checking the subscribers' data (as well as stakers' data if `config.STAKING_DOCS`
points to a JSON file in the DAO directory), the function `check_and_update_permission_dapp_boxes`
from the `foundation` module is run in regular intervals. A dedicated SystemD service on one of 
the ASA Stats servers has been installed for the purpose.
