#!/usr/bin/env python3

import json
import sys

import yaml


def main():
    config_yaml = None
    with open(sys.argv[1], "r") as stream:
        config_yaml = yaml.safe_load(stream)
    assume_role_arns = []
    for account in config_yaml["aws"]["accounts"]:
        if "assume_role_arn" in account:
            assume_role_arns.append(account["assume_role_arn"])
    print(json.dumps(assume_role_arns))


if __name__ == "__main__":
    main()
