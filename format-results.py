#! /usr/bin/env python

# This script pretty-prints Gradescope results to the console.

import argparse
import json

def colorize(text, score, possible):
    if score == 0:
        color = 31 # red
    elif score == possible:
        color = 32 # green
    else:
        color = 33 # yellow(ish)
    return '\x1b[1;%dm%s\x1b[0m' % (color, text)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--colorize' ,   dest='colorize', action='store_true', default=True)
    parser.add_argument('--no-colorize', dest='colorize', action='store_false')
    parser.add_argument('--quiet' ,      dest='quiet',    action='store_true')
    parser.add_argument('results',  default='results/results.json', nargs='?')
    args = parser.parse_args()

    with open(args.results) as file:
        results = json.load(file)

    total_earned   = 0
    total_possible = 0

    for test in results['tests']:
        score    = test['score']
        possible = test['max_score']
        title    = "%s (%d/%d)" % (test['name'], score, possible)

        total_earned   += score
        total_possible += possible

        if args.colorize:
            title = colorize(title, score, possible)
        print(title)
        if not args.quiet:
            print(test.get('output', ''))

    print()
    execution_time = results.get('execution_time')
    print('TOTAL TIME:  %ss' % execution_time)

    total_earned = results.get('score', total_earned)
    summary = 'TOTAL SCORE: %d/%d' % (total_earned, total_possible)
    if args.colorize:
        summary = colorize(summary, total_earned, total_possible)
    print(summary)
