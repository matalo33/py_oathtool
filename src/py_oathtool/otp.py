#!/usr/bin/python3

###
### Wrapper script to assist generating OTP codes with oathtool
### along with 2FA secrets stored in a YAML data file
###
import argparse
import datetime
import os
import oathtool
import platform
import subprocess
import sys
import time
import yaml

CODE_INTERVAL = 30 # seconds
DEFAULT_HOLDOFF = 5 # seconds
DEFAULT_CONFIG_PATH = os.path.join(os.path.expanduser('~'), '.otp-secrets.yaml')

def main():
  args = parse_args()
  config = read_config(args.secrets_file)

  if args.list_labels or args.tab_complete:
    print_labels(config, args)
    return

  print_code(config, args)


def parse_args():
  parser = argparse.ArgumentParser(description=(
    "Return a TOTP code for a provided label along with it's validity\n"
    "period. If the generated code is valid for %i or fewer seconds the\n"
    "script will pause and generate the next code.\n"
    "\n"
    "Hook your shell into 'otp -t' for tab completion\n"
    "\n"
    "Requires a YAML file with a list of secrets. By default the script looks at %s.\n"
    "\n"
    "This YAML file is expected to be formatted as follows:\n"
    "\n"
    "otpsecrets:\n"
    "  label-one: <secret>\n"
    "  another-code: <secret>\n"
    "  ...\n" % (DEFAULT_HOLDOFF, DEFAULT_CONFIG_PATH)
  ), formatter_class=argparse.RawTextHelpFormatter)

  parser.add_argument('label', nargs='?', help='the label to look up')
  parser.add_argument('-l', '--list-labels', help='list available labels', action='store_true')
  parser.add_argument('-t', '--tab-complete', help='list suitable for tab completion', action='store_true')
  parser.add_argument('-f', '--force', help='disable the <%i second holdoff feature' % DEFAULT_HOLDOFF, action='store_true')
  parser.add_argument('-s', '--secrets-file', help='secrets YAML file', default=DEFAULT_CONFIG_PATH)
  parser.add_argument('-m', '--minimalist', help='Don\'t print the time remaining for the current code', action='store_true')

  args = parser.parse_args()

  # Quit with error if -l or -t are missing and there is no label
  if not args.tab_complete and not args.list_labels and args.label == None:
    parser.error('You need to provide a label to look up when not using --list-labels or --tab-complete')

  if args.tab_complete and args.list_labels:
    parser.error('--list-labels and --tab-complete are mutually exclusive')

  return args


def read_config(path):
  # File exists?
  if not os.path.isfile(path):
    sys.exit('Could not find the secrets file at: %s' % path)

  # Try and parse for valid YAML
  try:
    with open(path, 'r') as file:
      config = yaml.safe_load(file)
  except yaml.YAMLError as error:
    if hasattr(error, 'problem_mark'):
      sys.exit('Problem parsing YAML\nError position: (%s:%s)' % (error.problem_mark.line + 1, error.problem_mark.column + 1))
    else:
      sys.exit(error)

  # Set a default holdoff value if one was not specified in the YAML file
  if 'holdoff' not in config:
    config['holdoff'] = DEFAULT_HOLDOFF

  return config


def print_labels(config, args):
  labels = []

  for label in config['otpsecrets'].keys():
    labels.append(label)

  labels.sort()

  if (args.list_labels):
    print('\n'.join(str(label) for label in labels))
  elif (args.tab_complete):
    print(' '.join(str(label) for label in labels))


def print_code(config, args):
  # Check the label exists
  if args.label not in config['otpsecrets']:
    print('Couldn\'t find label \'%s\' in the yaml. (Try the -l switch?)' % args.label)
    return

  # Wait for the next code if under the holdoff limit
  wait_for_next_code(config, args)

  # Get the current code
  code = oathtool.generate_otp(config['otpsecrets'][args.label])

  # Only print the code if requested
  if args.minimalist:
    print(code)
  else:
    print('%s\t(%dsec)' % (code, (CODE_INTERVAL - (datetime.datetime.now().second % CODE_INTERVAL))))

  # Put the code on the clipboard unless disabled or not printing to a terminal
  if ('use_clipboard' not in config or config['use_clipboard'] == False) and sys.stdout.isatty():
    copy_to_clipboard(config, code)


def wait_for_next_code(config, args):
  # Check how much time the current code has remaining and sleep if below the set holdoff threshold
  time_remaining = (CODE_INTERVAL - (datetime.datetime.now().second % CODE_INTERVAL))

  if not args.force and time_remaining < config['holdoff']:
    print('Short lived OTP. Holding off for %i second%s...' % (time_remaining, ('' if time_remaining == 1 else 's')))
    time.sleep(time_remaining)


def copy_to_clipboard(code):
  clipboard_program = None

  if platform.system() == 'Linux':
    # If on Linux determine if using X11 or Wayland
    clipboard_program = ['wl-copy'] if 'WAYLAND_DISPLAY' in os.environ else ['xclip', '-selection', 'clipboard']
  else:
    clipboard_program = ['pbcopy']

  try:
    process = subprocess.Popen(clipboard_program, stdin=subprocess.PIPE, text=True)
    process.stdin.write(code)
    process.stdin.close()
  except subprocess.CalledProcessError:
    print('Couldn\'t put code on the clipboard')


if __name__ == '__main__':
    main()
