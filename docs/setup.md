<a name="readme-top"></a>

# Setup Guide for Aegis

This guide will help you set up the development environment for `Aegis` using Python and Poetry.

## Prerequisites

Before getting started, ensure you have the following prerequisites installed:

1. **Python 3.8 or higher**: If you haven't installed Python yet, you can download the latest version from the [official Python website](https://www.python.org/downloads/). Follow the installation instructions for your operating system.

   #### Steps for Installing Python

   - **Windows**: Download the installer from the Python website and follow the installation wizard.
   - **macOS**: Python usually comes pre-installed. You may need to update it using Homebrew or install it manually.
   - **Linux**: Use your package manager to install Python. For example, on Ubuntu, you can use `apt`:
     ```bash
     sudo apt update
     sudo apt install python3
     ```

2. **Poetry**: Poetry is a dependency management and packaging tool for Python. Install it using pip:

   ```bash
   pip install poetry
   ```

   For more detailed instructions, refer to the [official Poetry documentation](https://python-poetry.org/docs/).

## Setting Up the Development Environment

1. **Clone the Repository**: First, clone the `Aegis` repository to your local machine using Git:

   ```bash
   git clone https://github.com/KarthikS373/aegis.git
   ```

2. **Change Directory**: Navigate to the `aegis` directory:

   ```bash
    cd aegis
   ```

3. **Install Dependencies**: Use Poetry to install the project dependencies:

   ```bash
    poetry install
   ```

4. **Activate the Virtual Environment**: Once the dependencies are installed, activate the virtual environment:

   ```bash
    poetry shell
   ```

5. **Run the Tests**: To ensure everything is set up correctly, run the tests:

   ```bash
    pytest
   ```

   If everything is set up correctly, you should see all the tests passing.

6. **Start Developing**: You're all set! You can now start developing `Aegis` on your local machine.

## Local Development Workflow

When working on `Aegis`, you can use the following commands to manage the development environment:

```bash
    poetry run aegis <command-name>
```

> For help on a specific command, use the `--help` flag. For example:
>
> ```bash
>  poetry run aegis --help
>  poetry run aegis <command-name> --help
> ```

## Next Steps

- **Read the Documentation**: To learn more about `Aegis`, refer to the [official documentation](../docs)
- **Examples**: Explore the [examples](examples/examples.md) to see how `Aegis` can be used in different scenarios
- **Get Help**: If you have any questions or need help, feel free to open an issue on the [GitHub repository](https://github.com/karthiks373/aegis/issues)
