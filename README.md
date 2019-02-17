# Log In Attempt Simulator
Simulation of regular log in activity on a site and random activity from hackers using brute-force password guessing attacks. 

## Assumptions
- The hackers try to avoid an account lockout by only testing a few username-password combinations rather than a full-blown dictionary attack. 
- The hackers have a good idea of the users and the format the usernames are in, but are guessing what they are exactly. 
- Each attack is standalone meaning the hacker carrying out a given attack doesn't keep track of which username-password combinations worked and which didn't, but each hacker (1 per attack) will choose to try to guess all the users or some subset of it. 
- The attacks come randomly. 
- Valid users come in a Poisson process hourly that depends on the day of the week and the time of day.
- Valid users have 1-3 IP addresses which are 4 random numbers on `[0, 255]` which don't have to be valid.
- Each hacker will use a single IP address which is generated in the same way the valid user ones are.
- Both valid users and hackers can make mistakes typing the user names--either forgetting a character or replacing a character with lowercase letter.
- Valid users are more likely to get their passwords and usernames correct than the hackers.
