"""Utility functions for the login attempt simulator."""

import ipaddress
import itertools
import json
import random
import string

def make_user_base(out_file):
    """Generate a user base and save it to a file."""
    with open(out_file, 'w') as user_base:
        for first, last in itertools.product(
            string.ascii_lowercase, ['smith', 'jones', 'kim', 'lopez', 'brown']
        ):
            user_base.write(first + last + '\n')
        for account in ['admin', 'master', 'dba']:
            user_base.write(account + '\n')

def get_valid_users(user_base_file):
    """Read in users from the user base file."""
    with open(user_base_file, 'r') as file:
        return [user.strip() for user in file.readlines()]

def random_ip_generator():
    """Randomly generate a fake IP address."""
    try:
        ip_address = ipaddress.IPv4Address('%d.%d.%d.%d' % tuple(
            random.randint(0, 255) for _ in range(4)
        ))
    except ipaddress.AddressValueError:
        ip_address = random_ip_generator()
    return str(ip_address) if ip_address.is_global \
        else random_ip_generator()

def assign_ip_addresses(user_list):
    """Assign users 1-3 fake IP addresses, returning a dictionary."""
    return {
        user: [
            random_ip_generator() for _ in range(random.randint(1, 3))
        ] for user in user_list
    }

def save_user_ips(user_ip_dict, file):
    """Save the mapping of users and their IP addresses to JSON file."""
    with open(file, 'w') as file:
        json.dump(user_ip_dict, file)

def read_user_ips(file):
    """Read in the JSON file of the user-IP address mapping."""
    with open(file, 'r') as file:
        return json.loads(file.read())
