import argparse
import os
import sys
import logging
import yaml
import dotenv

from taggedlist import TaggedLists, AnnotatedResults

def main():
    has_dotenv = True if os.environ.get('DOTENV') != None else False
    dotenv.load_dotenv(os.environ.get('DOTENV','.env'), verbose = has_dotenv, override = has_dotenv)
    parser = argparse.ArgumentParser(
        description='Tagged List Query Tool.',
        epilog='For details see https://github.com/matgoebl/taggedlistbrowser-cloud .')
    parser.add_argument('-r', '--readfiles',  default=os.environ.get('FILES'), help='Input file(s) to use, comma separated.' )
    parser.add_argument('-i', '--input',      default=None,              help='Select input model to use.')
    parser.add_argument('-t', '--tag',        default='.',               help='Work on value set of given tag or main key list.')
    parser.add_argument('-l', '--list',       action='store_true',       help='Output list.')
    parser.add_argument('-a', '--all',        action='store_true',       help='Output all.')
    parser.add_argument('-s', '--search',     default=None,              help='Filter list for items matching string (may contain *) or regular expression (if begins with /).')
    parser.add_argument('-f', '--filter',     default=None, nargs='+',   help='Filter list for items with TAG=VALUE.')
    parser.add_argument('-P', '--preannotation', action='store_true', default=(os.environ.get('PREANNOTATION','0') == "1"), help='Run initial preannotation.' )
    parser.add_argument('-T', '--tagspec', default=os.environ.get('TAGS'),    help='Use TagSpec.' )
    parser.add_argument('-D', '--docspec', default=os.environ.get('DOCSPEC'), help='Use DocSpec.' )
    parser.add_argument('-W', '--writeall',   default=None,              help='Write the whole model to a file.')
    parser.add_argument('-v', '--verbose',    action='count', default=int(os.environ.get('VERBOSE','0')), help="Be more verbose, can be repeated (up to 3 times)." )
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARNING-10*args.verbose,handlers=[logging.StreamHandler()],format="[%(levelname)s] %(message)s")

    if not args.readfiles:
        print("No input files specified.")
        sys.exit(1)

    model = TaggedLists()
    model.load_files(args.readfiles.split(','))

    if args.preannotation:
        result = model.query_valueset()
        annotatedresult = AnnotatedResults(model, result)
        tagspecs = { t.split("=")[0]: t.split("=")[-1] for t in args.tagspec.split(",")}
        annotatedresult.preannotate(tagspecs, args.docspec)
        if args.writeall:
            print(yaml.dump(annotatedresult.items))
            sys.exit(0)

    result = model.query_valueset(args.tag, args.input)

    annotatedresult = AnnotatedResults(model,result)

    if args.search:
        annotatedresult.search(args.search.split())

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
