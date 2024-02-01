import solcx
import sys

from clidantic import Parser
import numpy as np
from solcx import compile_standard, compile_source
from typing import Optional

from args import CompileArguments, ScanArguments
from cli import Effects
from config import BANNER
from model import predict, reverse_engineer_one_hot_encoding


def check_solcx() -> bool:
    """ Check if solc is installed """
    installed_versions = solcx.get_installed_solc_versions()
    if len(installed_versions) == 0:
        return False
    return True


def install_solcx(version=None) -> bool:
    """ Install solc """
    try:
        if version:
            # Install solc version
            solcx.install_solc(version)
            return True

        # Find latest solcx version
        latest_solcx_version = solcx.get_installable_solc_versions()[0]
        solcx.install_solc(latest_solcx_version)
        return True

    except:
        return False


def get_latest_installed_solcx_version() -> Optional[str]:
    """ Get the latest installed solcx version """
    try:
        latest_solcx_version = solcx.get_installed_solc_versions()[0]
        if latest_solcx_version:
            return latest_solcx_version

        raise Exception("Could not get latest solcx version")

    except:
        return None


def compile_solidity(contract):
    latest_solcx_version = get_latest_installed_solcx_version()

    if not latest_solcx_version:
        print("Could not get latest solcx version")
        return None

    try:
        compiled_file = compile_source(
            contract,
            output_values=["abi", "bin-runtime"],
            solc_version=latest_solcx_version
        )

        for key, value in compiled_file.items():
            name_of_contract = key
            abi = value['abi']
            bytecode = value['bin-runtime']

            return {
                "name": name_of_contract,
                "abi": abi,
                "bytecode": bytecode
            }

    except Exception as e:
        return None


def check_solidity_file(path: str) -> bool:
    if not path.endswith(".sol"):
        return False

    return True


def read_solidity_file(path: str):
    try:
        with open(path, "r") as f:
            contract_file = f.read()

        return contract_file

    except Exception as e:
        print("Error reading the file")
        sys.exit(1)


class Controller:
    def __init__(self):
        # Initialize the CLI parser and setup the commands
        self.cli = Parser(name="aegis")

        # Setup the commands
        self.setup_commands()

        # Initialize the cli typing effects
        self.effects = Effects()

        try:
            # Check if solc is installed
            is_solcx_installed = check_solcx()
            if not is_solcx_installed:
                print(BANNER)
                self.effects.skip_line(2)
                self.effects.write("Initializing Aegis CLI.....")

                # TODO: Suppress warnings
                successfully_installed = install_solcx()
                if successfully_installed:
                    self.effects.skip_line(1)
                    self.effects.write("Aegis CLI is ready to use")
                    self.effects.skip_line(2)
                else:
                    raise Exception("Could not install solc")

        except Exception as e:
            self.effects.write(
                "Something went wrong!!! Raise an issue on github")

    def setup_commands(self):
        commands = [
            # Command: info
            # Description: Get information about the application
            {
                "command": "info",
                "description": "Get information about the application",
                "script": self.info
            },

            # Command: scan
            # Description: Scan a file or directory for vulnerabilities
            {
                "command": "scan",
                "description": "Scan a file or directory for vulnerabilities",
                "script": self.scan
            },

            # Command: compile
            # Description: Compile the solidity code
            {
                "command": "compile",
                "description": "Compile the solidity code",
                "script": self.compile
            },
        ]
        for command in commands:
            self.cli.command(command["command"], command["description"])(
                command["script"])

    def info(self):
        print(BANNER)

        self.effects.skip_line(2)

        # Aegis
        self.effects.write("1. Aegis")
        self.effects.write(
            "Description: Aegis is a security tool for Ethereum smart contracts")

        self.effects.skip_line(2)

        # Solc
        self.effects.write("2. Solc")
        self.effects.write("Description: Solc is the solidity compiler")

        installed_versions = solcx.get_installed_solc_versions()
        latest_version = get_latest_installed_solcx_version()
        installed_path = solcx.get_solcx_install_folder()

        if len(installed_versions) == 0:
            self.effects.write("Solc is not installed")
        else:
            self.effects.write(f'Latest version: {latest_version}')
            self.effects.write(f'Installed versions: {installed_versions}')
            self.effects.write(f'Installed path: {installed_path}')

        # TODO: Slither

        # TODO: Mythril

        # TODO: Echidna

        self.effects.skip_line(2)

    def compile(self, args: CompileArguments):
        """ Compile the solidity code """
        is_solidity = check_solidity_file(args.path)
        if not is_solidity:
            print("Please provide a solidity file")
            return

        contract_file = read_solidity_file(args.path)

        self.effects.write("Compiling solidity code...")

        try:
            compiled_contract = compile_solidity(
                contract_file,
            )

            if not compiled_contract:
                raise Exception("Could not compile the solidity code")

            # TODO: Save the compiled contract to a file

        except Exception as e:
            print("Error compiling the solidity code")
            return

    def scan(self, args: ScanArguments):
        """ Scan a file or directory for vulnerabilities """
        is_solidity = check_solidity_file(args.path)
        if not is_solidity:
            print("Please provide a solidity file")
            return

        contract_file = read_solidity_file(args.path)

        try:
            compiled_contract = compile_solidity(
                contract_file,
            )

            if not compiled_contract:
                raise Exception("Could not compile the contract")

            self.effects.write("Scanning...")

            labels = {
                0: 'access-control',
                1: 'arithmetic',
                2: 'other',
                3: 'reentrancy',
                4: 'safe',
                5: 'unchecked-calls'
            }

            bytecode = compiled_contract["bytecode"]

            prediction = predict(bytecode)
            all_preds_np = np.array(prediction)
            original_labels = reverse_engineer_one_hot_encoding(all_preds_np)
            # print("Original Labels:", original_labels)
            mapped_labels = [[labels[label] for label in sublist]
                             for sublist in original_labels]
            # print("Mapped Labels:")
            for sublist in mapped_labels:
                print(sublist)

        except Exception as e:
            print("Error scanning!!! Please try again...")
            return
