# Login Attempt Simulator
Simulation of regular login activity on a site and random activity from hackers using brute-force password guessing attacks.

## Assumptions
- The hackers try to avoid an account lockout by only testing a few username-password combinations rather than a full-blown dictionary attack.
- The hackers have a good idea of the users and the format the usernames are in, but are guessing what they are exactly.
- Each attack is standalone meaning the hacker carrying out a given attack doesn't keep track of which username-password combinations worked and which didn't, but each hacker (1 per attack) will choose to try to guess all the users or some subset of it.
- The attacks come randomly.
- Valid users come in a Poisson process hourly that depends on the day of the week and the time of day.
- Valid users have 1-3 IP addresses which are 4 random integers in `[0, 255]`.
- Hackers will use either a single IP address for an attack or vary the IP address per username they attempt to log in with. This will be determined by the value passed with the `vary_ips` parameter to the `simulate()` method. These IP addresses are generated in the same way the valid user ones are.
- Both valid users and hackers can make mistakes typing the user names--either forgetting a character or replacing a character with lowercase letter.
- Valid users are more likely to get their passwords and usernames correct than the hackers.
- Although highly unlikely, it is possible the hacker has the same IP address as a valid user. The hacker may even be a valid user!

## Setup
```
# should install requirements.txt packages
pip install -e login-attempt-simulator # path to top level where setup.py is

# if not, install them explicitly
pip install -r requirements.txt
```

## Usage

### Create Userbase and IPs
```
import login_attempt_simulator as sim

user_base_file = 'user_data/user_base.txt'
user_ip_mapping_file = 'user_data/user_ips.json'

# create usernames and write to file
sim.utils.make_userbase(user_base_file)

# create one or more IP addresses per user and save mapping to file
valid_users = sim.utils.get_valid_users(user_base_file)
sim.utils.save_user_ips(
    sim.utils.assign_ip_addresses(valid_users), user_ip_mapping_file
)
```

### Simulate Over Time Period
*Note you can provide your own success probabilities when you instantiate the LogInAttemptSimulator.*
```
import datetime as dt

start = dt.datetime(2019, 2, 1, 7, 0)
end = start + dt.timedelta(days=10.5)

simulator = sim.LoginAttemptSimulator(user_ip_mapping_file, start, end)
simulator.simulate(attack_prob=0.01, try_all_users_prob=0.25, vary_ips=True)
```

### Save Logs for Analysis Later
```
simulator.save_hack_log('logs/attacks.csv')
simulator.save_log('logs/log.csv')
```
