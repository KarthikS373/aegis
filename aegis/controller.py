import solcx
import sys

from clidantic import Parser
from fpdf import FPDF
import numpy as np
from solcx import compile_standard, compile_source
from typing import Optional

from args import CompileArguments, ScanArguments, GenerateReportArguments
from cli import Effects
from config import BANNER
from helpers import Helper
from llm import llm
from model import predict, reverse_engineer_one_hot_encoding


class Controller:
    def __init__(self):
        # Initialize the CLI parser and setup the commands
        self.cli = Parser(name="aegis")

        # Setup the commands
        self.setup_commands()

        # Initialize the cli typing effects
        self.effects = Effects()

        # Setup the helper
        self.helper = Helper()

        try:
            # Check if solc is installed
            is_solcx_installed = self.helper.check_solcx()
            if not is_solcx_installed:
                print(BANNER)
                self.effects.skip_line(2)
                self.effects.write("Initializing Aegis CLI.....")

                # TODO: Suppress warnings
                successfully_installed = self.helper.install_solcx()
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
            # Command: summary
            # Description: Summarized a file or directory
            {
                "command": "summary",
                "description": "Get summary about the smart contract",
                "script": self.summary
            },
            # Command: compile
            # Description: Compile the solidity code
            {
                "command": "compile",
                "description": "Compile the solidity code",
                "script": self.compile
            },
            # Command: generate-report
            # Description: Generate a report for the scanned vulnerabilities
            {
                "command": "report",
                "description": "",
                "script": self.generate_report
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
        latest_version = self.helper.get_latest_installed_solcx_version()
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

    def summary(self, args: ScanArguments):

        is_solidity = self.helper.check_solidity_file(args.path)
        if not is_solidity:
            print("Please provide a solidity file")
            return

        contract_file = self.helper.read_solidity_file(args.path)

        prompt = """
            Analyze this "Solidity smart contract" code
            Provide a structured summary that includes: 
                (1) the contract's purpose and functionality; 
                (2) key components with their roles; 
                (3) mechanisms of user interaction and transaction flow;
                (4) notable security features or patterns employed;
            Aim for a concise, detailed, explanation to understand the contract's operation and use cases, remove any vague or ambiguous machine generated text.
            
            Contract: {}
        """.format(contract_file)

        for word in llm(prompt, stream=True):
            print(word, end='')

        # word = llm(prompt)
        # print(word)

        print("\n")

        return

    def compile(self, args: CompileArguments):
        """ Compile the solidity code """
        is_solidity = self.helper.check_solidity_file(args.path)
        if not is_solidity:
            print("Please provide a solidity file")
            return

        contract_file = self.helper.read_solidity_file(args.path)

        self.effects.write("Compiling solidity code...")

        try:
            compiled_contract = self.helper.compile_solidity(
                contract_file,
            )

            if not compiled_contract:
                print("No compiled contract found")
                raise Exception("Could not compile the solidity code")

        except Exception as e:
            print("Error compiling the solidity code")
            print(e)
            return

    def scan(self, args: ScanArguments):
        """ Scan a file or directory for vulnerabilities """
        is_solidity = self.helper.check_solidity_file(args.path)
        if not is_solidity:
            print("Please provide a solidity file")
            return

        contract_file = self.helper.read_solidity_file(args.path)

        try:
            compiled_contract = self.helper.compile_solidity(
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

            for entity in compiled_contract:
                bytecode = entity["bytecode"]

                print

                if not bytecode:
                    continue

                prediction = predict(bytecode)
                all_preds_np = np.array(prediction)
                original_labels = reverse_engineer_one_hot_encoding(
                    all_preds_np)

                mapped_labels = [[labels[label] for label in sublist]
                                 for sublist in original_labels]

                for sublist in mapped_labels:
                    def print_detailed_report(sublist):
                        self.effects.write("Scan complete...")
                        self.effects.skip_line(1)
                        self.effects.write("Scan report")
                        self.effects.write("-----------")

                        self.effects.write("Vulnerabilities:")
                        for label in sublist:
                            self.effects.write(f"{label}")
                            self.effects.write(f"--------------")

                            ed = self.helper.error_descriptions[label]
                            self.effects.write(
                                f"[desc]: {ed['desc']}"
                            )
                            self.effects.write(
                                f"[search]: {ed['search']}"
                            )
                            self.effects.skip_line(1)

                    def print_scan_result(sublist):
                        if 'safe' in sublist:
                            print("Smart contract scan complete - code looks safe")
                        else:
                            print_detailed_report(sublist)
                            # LLM Code for putting vulnerabilties:
                            prompt = """
                                    Can you say why and where is {} vulnerability in this code?:
                                    {}
                                    """.format(sublist[0], contract_file)

                            for word in llm(prompt, stream=True):
                                print(word, end='')

                    print_scan_result(sublist)

        except Exception as e:
            print("Error scanning!!! Please try again...")
            print(e)
            return

    def generate_report(self, args: GenerateReportArguments):
        is_solidity = self.helper.check_solidity_file(args.path)
        if not is_solidity:
            print("Please provide a solidity file")
            return

        pdf = FPDF()
        pdf.add_page()

        contract_file = self.helper.read_solidity_file(args.path)

        try:
            for iter in self.helper.generate_report_prompts:
                prompt = iter['instructions']
                title = iter['title']

                self.effects.write(f"Generating {title}...")
                try:
                    response = llm(f"{prompt} code: {contract_file}")
                    if response:
                        # Title
                        pdf.set_font('Arial', 'B', 16)
                        pdf.set_fill_color(200, 220, 255)
                        pdf.cell(0, 6, title, 'L', 1)

                        # line break
                        pdf.ln(4)

                        # Content
                        pdf.set_font('Arial', '', 12)
                        pdf.multi_cell(186, 6, response)

                except Exception as e:
                    print("Error generating {}".format(title))
                    print(e)
                    pass

            pdf.output('report.pdf', 'F')

        except Exception as e:
            print("Error generating report")
            print(e)
            return
