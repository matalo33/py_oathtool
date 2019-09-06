#!/usr/bin/python3

###
### Wrapper script to assist generating OTP codes with oathtool
### along with 2FA secrets stored in a YAML data file
###
import argparse
import os
import platform
import subprocess
import sys
import time
import yaml
from datetime import datetime
from argparse import RawTextHelpFormatter

HOLDOFF = 6

def main():
    parser = argparse.ArgumentParser(
        description=('''
    Return a TOTP code for a provided label along with it's validity
    period. If the generated code is valid for 6 or less seconds the
    script will pause and generate the next code.

    Hook your shell into 'otp -t' for tab completion

    Requires python packages
     * subprocess

    Requires oathtool on the command line
     * (mac) brew install oath-toolkit

    Requires a YAML file with a list of secrets. By default the script
    looks at ../data/otp-secrets.yaml relative to this script.

    YAML is expected to be encoded as follows:

    otpsecrets:
        label-one: <secret>
        another-code: <secret>
        ...'''),
        formatter_class=RawTextHelpFormatter
        )

    parser.add_argument('label', nargs='?', help='the label to look up')
    parser.add_argument('-l', '--list-labels', help='list available labels',
        action='store_true')
    parser.add_argument('-t', '--tab-complete', help='list suitable for tab completion',
        action='store_true')
    parser.add_argument('-f', '--force', help='disable the <5 second holdoff feature',
        action='store_true')
    parser.add_argument('-s', '--secrets-file', help='secrets YAML file')

    args = parser.parse_args()

    # Quit with error if -l or -t are missing and there is no label
    if not args.tab_complete and not args.list_labels and args.label == None:
        parser.error('You need to provide a label to look up when not using -l/-t')

    if args.tab_complete and args.list_labels:
        parser.error('You cannot provide -l & -t together')

    # Pick a YAML file
    if args.secrets_file:
        otpSecretsPath = args.secrets_file
    else:
        otpSecretsPath = os.path.join(os.path.expanduser("~"), '.otp-secrets.yaml')

    # File exists?
    if not os.path.isfile(otpSecretsPath):
        sys.exit('Could not find the secrets file at: '+otpSecretsPath)

    # Try and parse for valid YAML
    try:
        with open(otpSecretsPath, 'r') as infile:
            otpSecrets = yaml.safe_load(infile)
    except yaml.YAMLError as err:
        if hasattr(err, 'problem_mark'):
            mark = err.problem_mark
            print('Problem parsing YAML \nError position: (%s:%s)' % (mark.line+1, mark.column+1))
            sys.exit(1)
        else:
            sys.exit(err)

    if (args.list_labels or args.tab_complete):
        yamlLabels = []

        for label in otpSecrets['otpsecrets'].keys():
            yamlLabels.append(label)
        yamlLabels.sort()

        if (args.list_labels):
            print('\n'.join(str(x) for x in yamlLabels))
        elif (args.tab_complete):
            print(' '.join(str(x) for x in yamlLabels))

        sys.exit()

    # Update the holdoff value if one was specified in the YAML file
    if 'holdoff' in otpSecrets:
        global HOLDOFF
        HOLDOFF = otpSecrets['holdoff']

    # Check the label exists
    if args.label in otpSecrets['otpsecrets']:
        try:
            # Do some holdoff magic if the 30s window is almost up
            holdoffCheck = (30 - (datetime.now().second %30))
            if not args.force and holdoffCheck <= HOLDOFF:
                print('Short lived OTP. Holding off for %i second%s...' % (holdoffCheck, ('' if holdoffCheck == 1 else 's')))
                time.sleep(holdoffCheck)

            # Get the code
            totp = subprocess.check_output(['oathtool', '-b', '--totp', \
                otpSecrets['otpsecrets'][args.label]]).rstrip(b'\n')

            # Is this a number? Print it.
            try:
                print('%s\t(%dsec)' % (totp.decode(), (30 - (datetime.now().second %30))))

                # Try and put it on the clipboard unless disabled and printing to a terminal
                if ('use_clipboard' not in otpSecrets or otpSecrets['use_clipboard'] != False) and sys.stdout.isatty():
                    try:
                        program = ['xclip', '-selection', 'clipboard'] if platform.system() == 'Linux' else ['pbcopy']
                        process = subprocess.Popen(program, stdin=subprocess.PIPE)

                        process.stdin.write(totp)
                        process.stdin.close()
                    except subprocess.CalledProcessError as err:
                        print('Couldn\'t put on the clipboard')
            # Wasn't parsed as int, but maybe the output is useful?
            except ValueError:
                print('Output from oathtool doesn\'t seem to be valid')
                print('Here\'s the output anyway:\n')
                print(totp.decode())
        # Call to oathtool failed
        except subprocess.CalledProcessError as err:
            print(err.output)
            sys.exit(err.returncode)
    else:
        print('Couldn\'t find label \'%s\' in the yaml. (Try the -l switch?)' % args.label)

if __name__ == '__main__':
    main()
