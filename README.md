# Login Attempt Simulator
Simulation of regular login activity on a site and random activity from hackers using brute-force password guessing attacks. The login process involves a username and password (no additional validation).

## Assumptions
The simulator makes the following assumptions about valid users of the website:

- Valid users come according to a Poisson process with an hourly rate that depends on the day of the week and the time of day. A Poisson process models arrivals per unit time (hour here) as a Poisson distribution with mean λ (lambda) and the interarrival times are exponential distributed with mean 1/λ.
- Valid users connect from 1-3 IP addresses (unique identifier for devices using the Internet), which are 4 random integers in `[0, 255]` separated by periods. It is possible, although highly unlikely, that two valid users have the same IP address.
- Valid users are unlikely to make many mistakes entering their credentials.

The simulator makes the following assumptions about the hackers:

- The hackers try to avoid an account lockout by only testing a few username-password combinations rather than a full-blown dictionary attack (trying every password the hacker has in a dictionary of possible passwords that they maintain on every user). However, they don't add delays between their attempts.
- Since the hackers don't want to cause a denial of service, they limit the volume of their attacks and only make one attempt at a time.
- The hackers know the amount of accounts that exist in the system and have a good idea the format the usernames are in, but are guessing what they are exactly. They will choose to try to guess all 133 usernames or some subset of it.
- Each attack is standalone, meaning there is a single hacker acting for each attack.
- The hackers don't share information about which username-password combinations are correct.
- The attacks come randomly.
- Each hacker will use a single IP address, which is generated in the same way the valid user ones are. However, our simulator is capable of varying this IP address when `vary_ips=True` is passed to `simulate()`.
- Although highly unlikely, it is possible the hacker has the same IP address as a valid user. The hacker may even be a valid user.

## Setup
```shell
# should install requirements.txt packages
$ pip install -e login-attempt-simulator # path to top level where setup.py is

# if not, install them explicitly
$ pip install -r requirements.txt
```

## Usage

### Create Userbase and IPs
```python
>>> import login_attempt_simulator as sim

>>> user_base_file = 'user_data/user_base.txt'
>>> user_ip_mapping_file = 'user_data/user_ips.json'

# create usernames and write to file
>>> sim.utils.make_userbase(user_base_file)

# create one or more IP addresses per user and save mapping to file
>>> valid_users = sim.utils.get_valid_users(user_base_file)
>>> sim.utils.save_user_ips(
...     sim.utils.assign_ip_addresses(valid_users),
...     user_ip_mapping_file
... )
```

### Simulate Over Time Period
*Note you can provide your own success probabilities when you instantiate the `LoginAttemptSimulator`.*
```python
>>> import datetime as dt

>>> start = dt.datetime(2019, 2, 1, 7, 0)
>>> end = start + dt.timedelta(days=10.5)

>>> simulator = sim.LoginAttemptSimulator(user_ip_mapping_file, start, end)
>>> simulator.simulate(attack_prob=0.01, try_all_users_prob=0.25, vary_ips=True)
```

### Save Logs for Analysis Later
```python
>>> simulator.save_hack_log('logs/attacks.csv')
>>> simulator.save_log('logs/log.csv')
```
