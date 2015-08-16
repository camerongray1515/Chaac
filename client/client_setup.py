import configparser
import os
import bcrypt
import re

from binascii import hexlify

def start_setup_wizard():
    questions = [
        {"prompt": "What port would you like the server to run on?",
        "default": "4048",
        "validator": lambda x: x.isdigit() and int(x) > 1023 and
                int(x) <= 65535,
        "validation_error": "Value must be a number between 1024 and 65535 "
                "inclusive",
        "config_section": "Server",
        "config_key": "port"
        },

        {"prompt": "Enter a list of IP addresses allowed to connect to this "
            "client separated by commas.  If left empty, all IPs will be "
            "allowed",
        "default": "",
        "validator": lambda x: re.match(r"^((?:(?:25[0-5]|2[0-4][0-9]|[01]?"
                "[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"
                "((,(\ )?)(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
                "(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))*)?$", x) != None,
        "validation_error": "Value must be a comma separated list of valid IP "
                "addresses or nothing at all to allow all IPs",
        "config_section": "Security",
        "config_key": "allowed_ips"
        }
    ]

    config = configparser.ConfigParser()

    for question in questions:
        answer_invalid=True
        while answer_invalid:
            if question["default"] != None:
                question_string = "{0} [{1}]: ".format(question["prompt"],
                        question["default"])
            else:
                question_string = "{0}: ".format(question["prompt"])

            answer = input(question_string)
            print("")

            if answer == "":
                answer = question["default"]

            if question["validator"](answer):
                answer_invalid = False

                if question["config_section"] not in config:
                    config[question["config_section"]] = {}

                config[question["config_section"]]\
                        [question["config_key"]] = answer
            else:
                print("{0}".format(question["validation_error"]))

    authentication_key = generate_authentication_key()

    print("The authentication key for this client is:")
    print("\t" + authentication_key)
    print("You will need to enter this into the server when adding this "
            "client.  If you lose this key you will need to run setup "
            "again to generate a new one.")
    
    if "Security" not in config:
        config["Security"] = {}

    config["Security"]["authentication_key_hash"] = bcrypt.hashpw(
            authentication_key.encode("ascii"), bcrypt.gensalt()).decode(
                "ascii")

    with open("config.ini", "w") as f:
        config.write(f)

    answer_invalid=True
    while answer_invalid:
        start_server = input("Would you like to start the client now? (y/n): ")
        if start_server in ["y", "n"]:
            answer_invalid = False

    return start_server == "y"

def generate_authentication_key(n_bits=256):
    if n_bits % 8 != 0:
        raise ValueError("Number of bits must be divisible by 8")
    random_bytes = os.urandom(int(n_bits / 8))
    authentication_key = hexlify(random_bytes).decode("ascii")

    return authentication_key
