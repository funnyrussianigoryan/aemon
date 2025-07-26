import logging

from aemon.parser.parser import AemonCLIParser


def main():
    logging.basicConfig(level=logging.INFO)
    
    parser = AemonCLIParser()
    parser.parse_and_dispatch()

