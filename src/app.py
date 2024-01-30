from typing import Optional
from pydantic import BaseModel

from clidantic import Parser

cli = Parser(
    name="tea", description="_____ is a command line tool for scanning files for vulnerabilities")


@cli.command("scan", "Scan a file or directory for vulnerabilities")
def scan():
    """ Scan a file or directory for vulnerabilities """
    print(f"Scanning for vulnerabilities")


@cli.command("login", "Login to the application")
def login():
    """ Login to the application """
    print(f"Login to the application")


@cli.command("logout", "Logout of the application")
def logout():
    """ Logout of the application """
    print(f"Logout of the application")


@cli.command("help", "Get help on a command")
def help():
    """ Get help on a command """
    print(f"Get help on a command")


@cli.command("config", "Configure the application")
def config():
    """ Configure the application """
    print(f"Configure the application")


@cli.command("version", "Get the version of the application")
def version():
    """ Get the version of the application """
    print(f"Get the version of the application")


if __name__ == "__main__":
    cli()
