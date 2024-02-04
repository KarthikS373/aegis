import inquirer
import json
import os
import sys
import solcx

from solcx import compile_source
from typing import Optional
import re

class Helper:
    def __init__(self):
        self.error_descriptions = {
            'access-control': {
                'desc': "Access control vulnerabilities occur when smart contracts do not properly control access to sensitive functions or data.",
                'methods': "To mitigate access control vulnerabilities, ensure that sensitive functions or data can only be accessed by authorized users or contracts. Implement proper permission checks and access control mechanisms.",
                'search': "https://ethereum.stackexchange.com/questions/153133/question-about-access-control-vulnerability"
            },
            'arithmetic': {
                'desc': "Arithmetic vulnerabilities arise due to errors in mathematical calculations within smart contracts.",
                'methods': "To address arithmetic vulnerabilities, perform thorough testing and validation of mathematical operations. Implement safe arithmetic operations and consider using tested libraries for complex calculations.",
                'search': "https://consensys.github.io/smart-contract-best-practices/attacks/insecure-arithmetic"
            },
            'other': {
                'desc': "Other vulnerabilities refer to any issues in smart contracts that do not fit into specific categories such as access control or arithmetic.",
                'methods': "To address other vulnerabilities, conduct comprehensive code reviews and testing. Follow best practices for smart contract development and security.",
                'search': "https://www.cvedetails.com/vulnerability-list/vendor_id-17524/Ethereum.html"
            },
            'reentrancy': {
                'desc': "Reentrancy vulnerabilities occur when smart contracts are vulnerable to reentrant attacks, allowing an attacker to repeatedly call a function before previous calls are completed.",
                'methods': "To mitigate reentrancy vulnerabilities, implement proper locking mechanisms and ensure that critical state changes are completed before external calls are made. Use the withdrawal pattern for handling external transfers of funds.",
                'search': "https://stackoverflow.com/questions/tagged/reentrancy"
            },
            'safe': {
                'desc': "The absence of known vulnerabilities indicates that the smart contract code appears to be safe from common security threats.",
                'methods': "Continue to follow best practices for smart contract development and conduct regular security audits to maintain the code's safety.",
                'search': ""
            },
            'unchecked-calls': {
                'desc': "Unchecked calls vulnerabilities occur when smart contracts make external calls without properly validating or handling the return values.",
                'methods': "To address unchecked calls vulnerabilities, implement proper error handling and validation mechanisms for external calls. Use safe wrappers or libraries for interacting with external contracts.",
                'search': "https://www.bookstack.cn/read/ethereumbook-en/spilt.11.c2a6b48ca6e1e33c.md"
            }
        }

        self.generate_report_prompts = [
            {
                "title": "Summary",
                "description": "",
                "prompt": "Generate a detailed summary of the given solidity contract.",
                "instructions": "Please provide a concise summary outlining the purpose, functionality, and key components of the Solidity contract. Organize the summary into sections covering its main features, such as contract structure, functions, variables, and any notable dependencies."
            },
            {
                "title": "Vulnerabilities",
                "description": "",
                "prompt": "Identify and describe any vulnerabilities present in the Solidity contract.",
                "instructions": "Please list and describe any vulnerabilities detected within the Solidity contract's code. Highlight potential security risks, including but not limited to reentrancy issues, integer overflow/underflow, and unauthenticated function calls. Include recommendations for mitigating each vulnerability."
            },
            {
                "title": "Optimizations",
                "description": "",
                "prompt": "Suggest optimizations to enhance the performance and gas efficiency of the Solidity contract.",
                "instructions": "Propose specific optimizations aimed at improving the performance and gas efficiency of the Solidity contract. This may involve refactoring code to reduce gas costs, optimizing data structures and algorithms, and leveraging compiler optimizations. Provide clear instructions on implementing each optimization, ensuring compatibility with the contract's functionality."
            },
            {
                "title": "Additional",
                "description": "",
                "prompt": "Generate additional insights or analysis relevant to the Solidity contract.",
                "instructions": "Provide supplementary insights, analysis, or commentary pertinent to the Solidity contract. This may include comparisons with similar contracts, discussion of design decisions, or considerations for future enhancements. Tailor the content to address any specific concerns or interests relevant to the contract's stakeholders, ensuring clarity and relevance."
            }
        ]

    def check_solcx(self) -> bool:
        """ Check if solc is installed """
        installed_versions = solcx.get_installed_solc_versions()
        if len(installed_versions) == 0:
            return False
        return True

    def install_solcx(self, version=None) -> bool:
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

    def get_latest_installed_solcx_version(self) -> Optional[str]:
        """ Get the latest installed solcx version """
        try:
            latest_solcx_version = solcx.get_installed_solc_versions()[0]
            if latest_solcx_version:
                return latest_solcx_version

            raise Exception("Could not get latest solcx version")

        except:
            return None

    def compile_solidity(self, contract, optimize: bool = False):
        latest_solcx_version = self.get_latest_installed_solcx_version()

        if not latest_solcx_version:
            print("Could not get latest solcx version")
            return None

        try:
            compiled_file = compile_source(
                contract,
                output_values=["abi", "bin-runtime"],
                solc_version=latest_solcx_version
            )

            contracts = []
            for key, value in compiled_file.items():
                name_of_contract = key
                abi = value['abi']
                bytecode = value['bin-runtime']

                contracts.append({
                    "name": name_of_contract,
                    "abi": abi,
                    "bytecode": bytecode
                })

            return contracts

        except Exception as e:
            print(e)
            return None

    def check_solidity_file(self, path: str) -> bool:
        if not path.endswith(".sol"):
            return False

        return True

    def read_solidity_file(self, path: str):
        try:
            with open(path, "r") as f:
                contract_file = f.read()

            return contract_file

        except Exception as e:
            print("Error reading the file")
            sys.exit(1)

    def write_solidity_file(self, path: str, content: str):
        try:
            # Create the directory if it doesn't exist
            directory = os.path.dirname(path)
            if not os.path.exists(directory):
                os.makedirs(directory)

            # Modify the path and content
            path = path.replace('<stdin>:', '')

            if not isinstance(content, str):
                content = json.dumps(content)

            # Write to the file
            with open(path, "w") as f:
                f.write(content)

        except Exception as e:
            print("Error writing the file")
            print(e)
            sys.exit(1)

    def generateInquirer():

        categories = {
    "governance": {
        "DAOs": ["Voting", "Proposals", "Quadratic Voting", "Delegated Voting", "Snapshot Voting"],
        "Treasury Management": ["Multi-sig Wallets", "Funding Proposals", "Spending Limits", "Budget Tracking"],
        "Governance Tokens": ["Mintable", "Burnable", "Pausable", "Vesting", "Token-Curated Registries"],
    },
    "defi": {
        "Lending/Borrowing": ["Collateralized Loans", "Undercollateralized Loans", "Interest Rate Models", "Flash Loans"],
        "DEX": ["Automated Market Maker (AMM)", "Order Book", "Liquidity Pools", "Cross-Chain Swaps"],
        "Yield Farming": ["Staking", "LP Tokens", "Reward Distribution", "Auto-Compounding"],
        "Stablecoins": ["Collateralized", "Algorithmic", "Rebase Mechanisms", "Stability Mechanisms"],
        "Derivatives": ["Options", "Futures", "Synthetics", "Perpetuals"],
    },
    "token": {
        "ERC20": ["Burnable", "Mintable", "Pausable", "Fee on Transfer"],
        "ERC721": ["Burnable", "Royalties", "Ownable", "Mintable", "Metadata Updatable"],
        "ERC1155": ["Burnable", "Royalties", "Pausable", "Batch Transfer"],
        "Governance Tokens": ["Voting Rights", "Delegation", "Timelock", "Governance with EIP-712"],
        "Utility Tokens": ["Access Rights", "Discounts", "Membership", "Service Access"],
    },
    "marketplace": {
        "Marketplace": ["Auction", "Fixed Price", "Offers", "Reserve Price"],
        "NFT Marketplace": ["Royalties", "Batch Upload", "Metadata Standards", "Lazy Minting"],
        "DeFi Marketplace": ["Token Swaps", "Liquidity Provision", "Fee Models", "Automated Portfolio Management"],
    },
    "airdrop": {
        "Airdrop": ["Timed Release", "Merit Based", "Random", "Snapshot Based", "Activity Based"],
        "Token Distribution": ["Linear Vesting", "Cliff Vesting", "Immediate", "Performance Based"],
    },
    "miscellaneous": {
        "Privacy": ["Zero Knowledge Proofs", "Private Transactions", "Tornado Cash"],
        "Layer 2": ["State Channels", "Plasma", "Optimistic Rollups", "ZK Rollups"],
        "Interoperability": ["Cross-Chain Bridges", "Wrapped Tokens", "Chain Agnostics"],
        "Oracles": ["Data Feeds", "Decentralized Oracles", "Off-Chain Computation"],
        "Security": ["Auditing Tools", "Smart Contract Monitors", "Bug Bounties"],
        "Storage": ["IPFS", "Filecoin", "Arweave", "Decentralized Storage Solutions"],
        "Identity": ["DID (Decentralized Identifiers)", "Verifiable Credentials", "Self-Sovereign Identity"],
        "Social Networks": ["Decentralized Social Media", "Token-Based Incentives", "Decentralized Content Creation"],
        "Games and Collectibles": ["GameFi", "Play to Earn", "Virtual Worlds", "Digital Collectibles"],
        "Insurance": ["Decentralized Insurance", "Smart Contract Cover", "Parametric Insurance"],
        "Supply Chain": ["Track and Trace", "Proof of Origin", "Supply Chain Finance"],
    }

        }

        # Step 1: Choose the category
        category_questions = [
            inquirer.List('category',
                        message="Select the category of the contract",
                        choices=list(categories.keys())),
        ]
        category = inquirer.prompt(category_questions)['category']

        # Step 2: Choose the type of smart contract within the selected category
        contract_types = list(categories[category].keys())
        contract_type_questions = [
            inquirer.List('contract_type',
                        message="Select the type of Solidity smart contract you want to build",
                        choices=contract_types),
        ]
        contract_type = inquirer.prompt(contract_type_questions)['contract_type']

        # Step 3: Choose modifications or plugins for the selected contract type
        modifications = categories[category][contract_type]
        mod_questions = [
            inquirer.Checkbox('mods',
                            message=f"Select modifications/plugins to add to the {contract_type} contract",
                            choices=modifications),
        ]
        mods_selected = inquirer.prompt(mod_questions)['mods']

        # Step 4: Input additional details about the contract
        detail_questions = [
            inquirer.Text('name', message="Enter the name of the contract"),
            inquirer.Text('token', message="Enter the token symbol (if applicable)"),
            inquirer.Text('description', message="Enter a description of the contract"),
        ]
        details = inquirer.prompt(detail_questions)


        # Print all responses
        print("\nSummary of your selections:")
        print(f"Contract Type: {contract_type}")
        print(f"Modifications/Plugins: {', '.join(mods_selected) if mods_selected else 'None'}")
        print(f"Name of Contract: {details['name']}")
        print(f"Token Symbol: {details['token']}")
        print(f"Description: {details['description']}")

        return category,contract_type, {', '.join(mods_selected) if mods_selected else 'None'}, details['name'], details['token'], details['description']
    import re

    def extract_code_and_write_to_file(response):
        # Define a regular expression pattern to match content within triple backticks
        pattern = r"```(?:solidity)?([\s\S]+?)```"
    
        # Find all matches of the pattern in the response
        matches = re.findall(pattern, response)
        
        
        if matches:
            # Assume there is only one code block in the response for simplicity
            code_content = matches[0]
            
        else:
            print("No code block found in the response")

        rest_of_text = re.sub(pattern, "", response)
        return code_content, rest_of_text
            

