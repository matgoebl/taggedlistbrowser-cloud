import argparse
import os
import sys
import logging
import yaml

from taggedlist import TaggedLists, AnnotatedResults

def main():
    parser = argparse.ArgumentParser(
        description='Tagged List Query Tool.',
        epilog='For details see https://github.com/matgoebl/taggedlistbrowser-cloud .')
    parser.add_argument('-r', '--readfiles',  nargs='*',                 help='Input file(s) to use.',  default=os.environ.get('INPUTFILES') )
    parser.add_argument('-i', '--input',      default=None,              help='Select input model to use.')
    parser.add_argument('-t', '--tag',        default='.',               help='Work on value set of given tag or main key list.')
    parser.add_argument('-l', '--list',       action='store_true',       help='Output list.')
    parser.add_argument('-a', '--all',        action='store_true',       help='Output all.')
    parser.add_argument('-s', '--search',     default=None,              help='Filter list for items beginning with string or regular expression (if it contains a "*").')
    parser.add_argument('-f', '--filter',     default=None, nargs='+',   help='Filter list for items with TAG=VALUE.')
    parser.add_argument('-v', '--verbose',    action='count', default=0, help="Be more verbose, can be repeated (up to 3 times).")
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARNING-10*args.verbose,handlers=[logging.StreamHandler()],format="[%(levelname)s] %(message)s")

    if not args.readfiles:
        print("No input files specified.")
        sys.exit(1)

    model = TaggedLists()
    model.load_files(args.readfiles)

    result = model.query_valueset(args.tag, args.input)

    annotatedresult = AnnotatedResults(model,result)

    if args.search:
        annotatedresult.search(args.search)

    annotatedresult.annotate()

    if args.filter:
        annotatedresult.filter(args.filter)

    if args.list:
        print('\n'.join(annotatedresult.keys()))
        sys.exit(0)

    if args.all:
        print(yaml.dump(annotatedresult.results(),default_flow_style=False,encoding=None,width=160, indent=4))
        sys.exit(0)

    sys.exit(0)


if __name__ == '__main__':
    main()
