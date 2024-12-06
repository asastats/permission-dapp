from pathlib import Path

from algosdk.v2client.algod import AlgodClient

from permissiondapp.helpers import compile_program, environment_variables, private_key_from_mnemonic
from permissiondapp.network import create_app


def deploy_app():
    env = environment_variables()

    algod_client = AlgodClient(env.get("algod_token"), env.get("algod_address"))
    creator_private_key = private_key_from_mnemonic(env.get("creator_mnemonic"))

    approval_program_source = (
        open(Path(__file__).resolve().parent / "artifacts" / "approval.teal")
        .read()
        .encode()
    )
    clear_program_source = (
        open(Path(__file__).resolve().parent / "artifacts" / "clear.teal")
        .read()
        .encode()
    )

    # compile programs
    approval_program = compile_program(algod_client, approval_program_source)
    clear_program = compile_program(algod_client, clear_program_source)

    # create new application
    app_id = create_app(
        algod_client, creator_private_key, approval_program, clear_program
    )
    # print("App ID: ", app_id)
    return app_id


if __name__ == "__main__":
    deploy_app()
