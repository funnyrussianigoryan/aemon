import logging

from aemon.core.dispatcher import CommandDispatcher
from aemon.parser.parser import AemonCLIParser


def main():
    logging.basicConfig(level=logging.INFO)
    
    # Parse command line arguments to get DTO
    parser = AemonCLIParser()
    command_args = parser.parse()
    
    # Dispatch and execute the command
    dispatcher = CommandDispatcher()
    dispatcher.dispatch(command_args)

