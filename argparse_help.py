#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import argparse
import sys

def ratioFloat (string):
    value = float(string)
    if value < 0 or value > 1:
        raise argparse.ArgumentTypeError('Value of a ration has to be between 0 and 1.')
    return value

class _HelpAction(argparse._HelpAction):

    def __call__(self, parser, namespace, values, option_string=None):
        parser.print_help()

        # retrieve subparsers from parser
        subparsers_actions = [
            action for action in parser._actions
            if isinstance(action, argparse._SubParsersAction)]
        # there will probably only be one subparser_action,
        # but better save than sorry
        print
        for subparsers_action in subparsers_actions:
            # get all subparsers and print help
            for choice, subparser in subparsers_action.choices.items():
                print("Positional argument '{}':".format(choice))
                print(subparser.format_help())

        parser.exit()

def set_default_subparser(self, name, args=None):
    """default subparser selection. Call after setup, just before parse_args()
    name: is the name of the subparser to call by default
    args: if set is the argument list handed to parse_args()

    , tested with 2.7, 3.2, 3.3, 3.4
    it works with 2.6 assuming argparse is installed
    """
    subparser_found = False
    existing_default = False
    for arg in sys.argv[1:]:
        if arg in ['-h', '--help']:  # global help if no subparser
            break
    else:
        for x in self._subparsers._actions:
            if not isinstance(x, argparse._SubParsersAction):
                continue
            for sp_name in x._name_parser_map.keys():
                if sp_name in sys.argv[1:]:
                    subparser_found = True
                if sp_name == name:
                    existing_default = True
        if not subparser_found:
            # insert default in first position, this implies no
            # global options without a sub_parsers specified
            if not existing_default:
                for x in self._subparsers._actions:
                    if not isinstance(x, argparse._SubParsersAction):
                        continue
                    x.add_parser(name)
                    break
            self.add_argument("--dummy-subparser-guard", action = "store_true")
            if args is None:
                sys.argv.insert(len(sys.argv), name)
            else:
                args.insert(len(args), name)

