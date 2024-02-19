import numpy
import json
import argparse
import mb_interpreter

def main():
    parser = argparse.ArgumentParser(description='MolBench Benchmarking Suite')

    parser.add_argument('--script', '-s', action='store', help='The MolBench script that you want to execute. Writing .mb scripts is specified in --script-doc, -d')
    parser.add_argument('--benchmark', '-b', action='store', help='The benchmark that you want to load.')
    parser.add_argument('--action', '-a', action='store', help='The action declarator.')

    args = parser.parse_args()
    
    if all(not a for _, a in vars(args).items()):
        print(f"Please give at least argument. Consult the --help option if you are struggling.")
        return

    if args.script:
        mb_interpreter.handle_script(args.script)
        return



if __name__ == '__main__':
    main()
