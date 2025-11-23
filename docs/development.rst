Development
===========

Setup
-----

Starting with version `0.6`, and due to new requirements including Algokit, the Permission dApp requires Python 3.12 or later for development and deployment.


Python environment
^^^^^^^^^^^^^^^^^^

Create Python virtual environment:

.. code-block:: bash

  python3 -m venv dapp


Activate Python environment:

.. code-block:: bash

  source dapp/bin/activate


Adding an alias can be useful:

.. code-block:: bash
  :caption: ~/.bashrc

  alias 'dapp'='cd /home/ipaleka/dev/permission-dapp/dapp; \
    source /home/ipaleka/dev/venvs/dapp/bin/activate'


Environment variables
^^^^^^^^^^^^^^^^^^^^^

Copy provided .env.example file to a working copy:

.. code-block:: bash

  cd /home/ipaleka/dev/permission-dapp/dapp
  cp .env.example .env

You have to update `CREATOR_TESTNET_MNEMONIC` variable in the newly created `.env`` file, 
as well as the related `PERMISSION_APP_ID_TESTNET` application identifier after you deploy your own dapp on Testnet.


SonarQube
^^^^^^^^^

`SonarQube <https://docs.sonarsource.com/sonarqube-community-build>`_
is an automated code review and static analysis tool designed to detect coding issues.
You can find the installation instructions
`here <https://docs.sonarsource.com/sonarqube-community-build/try-out-sonarqube>`_


Starting server
"""""""""""""""

.. code-block:: bash

  $ ~/opt/pt/sonarqube-25.9.0.112764/bin/linux-x86-64/sonar.sh console


Starting scanner
""""""""""""""""

For additional information read the scanner 
`documentation <https://docs.sonarqube.org/latest/analysis/scan/sonarscan>`_.

You should add scanner executable to your PATH. For example, by adding the following
line to your ``~/.bashrc``:

.. code-block:: bash

  export PATH=$PATH:~/opt/repos/sonar-scanner/bin


To start scanning, run the scanner from the root directory of the project with:

.. code-block:: bash

  $ sonar-scanner


Newer versions require authentication:

.. code-block:: bash

  $ sonar-scanner -Dsonar.login=admin -Dsonar.password=password -Dsonar.projectKey=permission-dapp


Smart contract
--------------

Compile
^^^^^^^

After you activated the Python environment, you can compile smart contract by issuing the following commands:

.. code-block:: bash

  algokit compile py contract.py --out-dir artifacts


Deploy, fund, and setup dApp
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Here's a shortcat Django management command that will deploy generated smart contract on the blockchain,
fund the related account with required ALGO, and finally set up the dApp with rewards token ID and
claim period duration values retrieved from the environemnt variables:

.. code-block:: bash

  python ........


Tests
-----

Python
^^^^^^

.. code-block:: bash

  cd /home/ipaleka/dev/permission-dapp/dapp
  source /home/ipaleka/dev/venvs/dapp/bin/activate
  python -m pytest -v  # or just `pytest -v`
