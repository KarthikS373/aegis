import sys
import time

from colorama import init


class Effects:
    def __init__(self):
        init(autoreset=True)

    def typewriter_effect(self, text, delay=0.05):
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)
        print()

    def skip_line(self, number_of_lines=1):
        for i in range(number_of_lines):
            print()

    def welcome_animation(self):
        self.typewriter_effect("Initializing Aegis CLI.....")
        time.sleep(1)
        self.typewriter_effect("Welcome to Aegis CLI !!!")
        time.sleep(1)
        self.typewriter_effect("Type 'help' to see available commands")
        time.sleep(1)

        print()
        print()
        print()

    def write(self, text):
        self.typewriter_effect(text)
        time.sleep(0.5)

    def loading_animation(self):
        while True:
            for char in '|/-\\':
                sys.stdout.write('\r' + 'Generating' + char)
                time.sleep(0.1)
                sys.stdout.flush()
