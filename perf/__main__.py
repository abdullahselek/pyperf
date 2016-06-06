import argparse
import json
import sys

import perf


def parse_args():
    parser = argparse.ArgumentParser(description='Display benchmark results.')
    parser.add_argument('-v', '--verbose', action="store_true",
                        help='an integer for the accumulator')
    parser.add_argument('filenames', metavar="filename", type=str, nargs="+",
                        help='name of JSON files')
    return parser.parse_args()


def parse_file(results, runs, fp):
    for line in fp:
        line = line.strip()
        if not line:
            # ignore empty lines
            continue

        data = json.loads(line)
        if 'run_result' in data:
            run = perf.RunResult._from_json(data['run_result'])
            runs.append(run)
        elif 'results' in data:
            result = perf.Results._from_json(data['results'])
            results.append(result)
        else:
            print("ERROR: invalid JSON")
            sys.exit(1)


def parse_results(args):
    results = []
    runs = []
    for filename in args.filenames:
        if filename != '-':
            fp = open(filename)
        else:
            fp = sys.stdin
        with fp:
            parse_file(results, runs, fp)

    if runs:
        result = perf.Results(runs=runs)
        results.append(result)

    if not results:
        print("ERROR: no result JSON read from stdin")
        sys.exit(1)
    return results


def display_result(args, results):
    if result.metadata:
        print("Metadata:")
        for key, value in sorted(result.metadata.items()):
            print("- %s: %s" % (key, value))

    if args.verbose:
        nrun = len(result.runs)
        for index, run in enumerate(result.runs, 1):
            text = ', '.join(perf._format_timedeltas(run.samples))
            text = 'runs (%s): %s' % (len(run.samples), text)
            if run.warmups:
                text = ('warmup (%s): %s; %s'
                        % (len(run.warmups),
                           ', '.join(perf._format_timedeltas(run.warmups)),
                           text))

            print("Run %s/%s: %s" % (index, nrun, text))

    print("Average: %s" % result.format(verbose=args.verbose))


args = parse_args()
results = parse_results(args)
for result in results:
    display_result(args, result)
