# py_oathtool

A python wrapper script around oathtool to allow for easy OTP code generation on the command line.

This project was born out of my frustration of having many many 2-Factor accounts on my mobile phone, which did not present a quick and easy mechanism to generate and use codes.

Tested only on Mac (for now).

## Installation

`pip install py_oathtool`

## Dependencies

* Python packages
    * subprocess32

**oathtool** should be available on the PATH

* Mac: `brew install oath-toolkit`
* Linux: `xclip` for clipboard support

## Usage

List the configured accounts with the **-l** switch.

    $ otp -l
    github
    aws-account-dev
    aws-account-prod

Generate an OTP by providing the account name. The script will provide the OTP code, and also drop it to the clipboard.

    $ otp aws-account-dev
    129987
    Valid for 18 more seconds
    (On the clipboard!)

If a code is only valid for a short duration the script will pause until the next 30-second window begins.

    $ otp cr-dev
    Short lived OTP. Holding off for 4 seconds...
    591658
    Valid for 30 more seconds
    (On the clipboard!)

Read about all options

    $ otp -h

## Configuration

Two pieces of information are required for each account:

* An account name / label
* Your 64 character oath secret provided by the 3rd party. This is typically a QR code, but websites often also offer the string.

The script will read these values from a config file sourced from, by default, **~/.otp-secrets.yaml** in the following format:

    otpsecrets:
      github: IOOVV6U5AUHUISZKJNVCCG4JWUR5XDFSI7ND62A7QT5ZOEVYVA7JEEDKTG3ZM57B
      aws-account-dev: XQYNZOIA4PWCTJCB9654EQP5LUIP23BOW6J5ZIRZZSDHK24AUEDUSCONP3KQQY4N
      aws-account-prod: 57QPXJFJ4D2ILQBRZGSHKAZCJ2Y46C52FGVSZRYMY7UMWTIQI6I3GOJQZ4VJN2R4

## Disclaimer

2-Factor is meant to provide an extra layer of account security and this tool does not exactly promote that concept. You should be responsible for taking reasonable steps to protect your secrets file, and perhaps this is not the ideal 2-Factor solution for your most important accounts.

I take no responsibility if you lose accounts through using this tool.

## Building

To follow...

pip install --user -e .