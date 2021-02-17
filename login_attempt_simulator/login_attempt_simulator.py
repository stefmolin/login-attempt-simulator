"""Simulator of login attempts from valid users and hackers."""

import calendar
import datetime as dt
from functools import partial
import math
import random
import string

import numpy as np
import pandas as pd

from .utils import random_ip_generator, read_user_ips

class LoginAttemptSimulator:
    """
    Class for simulating login attempts from valid and nefarious users.

    Class attributes:
        - ATTEMPTS_BEFORE_LOCKOUT: Number of consecutive failed attempts
                                   before lockout.
        - ACCOUNT_LOCKED: Error message for log when account is locked.
        - WRONG_USERNAME: Error message for log when username is wrong.
        - WRONG_PASSWORD: Error message for log when password is wrong.

    Instance attributes:
        - user_base: Dictionary mapping usernames to their IP addresses.
        - users: The list of usernames in the user_base.
        - start: The start datetime for the simulation.
        - end: The end datetime for the simulation.
        - hacker_success_likelihoods: List of probabilities of successful log
                                      in for hacker. Length of this list is
                                      also max attempts hacker will make per
                                      user attempted.
        - valid_user_success_likelihoods: List of probabilities of successful
                                          login for valid users. Length of
                                          this list is also max attempts user
                                          will make.
        - log: Pandas DataFrame recording all login attempts and their outcome.
        - hack_log: Pandas DataFrame recording when attacks occurred.
        - locked_accounts: List of accounts currently locked.
    """

    ATTEMPTS_BEFORE_LOCKOUT = 3
    ACCOUNT_LOCKED = 'error_account_locked'
    WRONG_USERNAME = 'error_wrong_username'
    WRONG_PASSWORD = 'error_wrong_password'

    def __init__(self, user_base_json_file, start, end=None, *,
                 attacker_success_probs=[.25, .45],
                 valid_user_success_probs=[.87, .93, .95],
                 seed=None
                ):
        """
        Create a simulator.

        Parameters:
            - user_base_json_file: The JSON file name of the mapping of
                                  usernames to their IPs.
            - start: The start datetime for the simulation.
            - end: The end datetime for the simulation.
            - attacker_success_probs: List of probabilities of successful log
                                      in for hacker. Length of this list is
                                      also max attempts hacker will make per
                                      user attempted.
            - valid_user_success_probs: List of probabilities of successful
                                        login for valid users. Length of
                                        this list is also max attempts user
                                        will make.
            - seed: Value to use as a seed for random number generation.

        Returns:
            A `LoginAttemptSimulator` object.
        """
        self.user_base = read_user_ips(user_base_json_file) # user, ip address dict
        self.users = [user for user in self.user_base.keys()]

        self.start = start
        self.end = end if end else self.start + dt.timedelta(days=random.uniform(1, 50))

        self.hacker_success_likelihoods = attacker_success_probs
        self.valid_user_success_likelihoods = valid_user_success_probs

        self.log = pd.DataFrame(
            columns=[
                'datetime', 'source_ip', 'username',
                'success', 'failure_reason'
            ]
        )
        self.hack_log = pd.DataFrame(
            columns=['start', 'end', 'source_ip']
        )

        self.locked_accounts = []

        # we are using numpy and random for random numbers so we set 2 seeds:
        random.seed(seed)
        np.random.seed(seed)

    def _record(self, when, source_ip, username, success, failure_reason):
        """
        Record the outcome of a login attempt.

        Parameters:
            - when: The datetime of the event.
            - source_ip: The IP address where the attempt came from.
            - username: The username used in the attempt.
            - success: Whether or not the attempt succeeded (Boolean).
            - failure_reason: The reason for the failure, if failed.

        Returns:
            None, the `log` attribute is updated.
        """
        self.log = self.log.append({
            'datetime': when,
            'source_ip': source_ip,
            'username': username,
            'success': success,
            'failure_reason': failure_reason
        }, ignore_index=True)

    def _attempt_login(self, when, source_ip, username,
                       username_accuracy, success_likelihoods
                      ):
        """
        Simulates a login attempt, allowing for account lockouts, and
        recording the results.

        Parameters:
            - when: The datetime to start trying.
            - source_ip: The IP address where the attempt is coming from.
            - username: The username being used in the attempt.
            - username_accuracy: The probability the username is correct.
            - success_likelihoods: A list of the probabilities of the password
                                   being correct. The number of attempts to
                                   log in will be equal to the length of this
                                   list.

        Returns:
            The datetime after trying.
        """
        current = when
        recorder = partial(self._record, source_ip=source_ip)

        if random.random() > username_accuracy:
            # username will be provided incorrectly
            correct_username = username
            username = self._distort_username(username)

        if username not in self.locked_accounts:
            tries = len(success_likelihoods)
            for i in range(min(tries, self.ATTEMPTS_BEFORE_LOCKOUT)):
                current += dt.timedelta(seconds=1)

                if username not in self.users:
                    recorder(
                        when=current,
                        username=username,
                        success=False,
                        failure_reason=self.WRONG_USERNAME
                    )
                    if random.random() <= username_accuracy:
                        # corrects username
                        username = correct_username
                    continue

                if random.random() <= success_likelihoods[i]:
                    # successfully logs in
                    recorder(
                        when=current,
                        username=username,
                        success=True,
                        failure_reason=None
                    )
                    break
                else:
                    recorder(
                        when=current,
                        username=username,
                        success=False,
                        failure_reason=self.WRONG_PASSWORD
                    )
            else:
                # lock user out if max attempts was exceeded
                # (has to fail to get here)
                if tries >= self.ATTEMPTS_BEFORE_LOCKOUT and username in self.users:
                    self.locked_accounts.append(username)
        else:
            recorder(
                when=current,
                username=username,
                success=False,
                failure_reason=self.ACCOUNT_LOCKED
            )
            # unlock the account randomly
            if random.random() >= .5:
                self.locked_accounts.remove(username)
        return current
    
    def _hacker_attempts_login(self, when, source_ip, username):
        """
        Simulates a login attempt from an attacker.

        Parameters:
            - when: The datetime to start trying.
            - source_ip: The IP address where the attempt is coming from.
            - username: The username being used in the attempt.

        Returns:
            The datetime after trying.
        """
        return self._attempt_login(
            when=when,
            source_ip=source_ip,
            username=username,
            username_accuracy=random.gauss(mu=0.35, sigma=0.5),
            success_likelihoods=self.hacker_success_likelihoods
        )

    def _valid_user_attempts_login(self, when, username):
        """
        Simulates a login attempt from a valid user.

        Parameters:
        - when: The datetime to start trying.
        - source_ip: The IP address where the attempt is coming from.
        - username: The username being used in the attempt.

        Returns:
            The datetime after trying.
        """
        return self._attempt_login(
            when=when,
            source_ip=random.choice(self.user_base[username]),
            username=username,
            username_accuracy=random.gauss(mu=1.01, sigma=0.01),
            success_likelihoods=self.valid_user_success_likelihoods
        )

    @staticmethod
    def _distort_username(username):
        """
        Alters the username to allow for wrong username login failures.
        Randomly removes a letter or replaces a letter in a valid username.
        """
        username = list(username)
        change_index = random.randint(0, len(username) - 1)
        if random.random() < .5:
            # remove random letter
            username.pop(change_index)
        else:
            # randomly replace a single letter
            username[change_index] = random.choice(string.ascii_lowercase)
        return ''.join(username)

    @staticmethod
    def _valid_user_arrivals(when):
        """
        Static method for simulating the Poisson process of arrivals
        (users wanting to log in to the website). Lambda for the Poisson
        varies depending upon the day and time of week.

        Parameters:
            - when: The datetime to determine hourly arrivals
                    and interarrival time for.

        Returns:
            The arrivals in that given hour and the interarrival time,
            which could put the arrivals outside the hour itself.
        """
        is_weekday = when.weekday() not in (calendar.SATURDAY, calendar.SUNDAY)
        late_night = when.hour < 5 or when.hour >= 11
        work_time = is_weekday and (when.hour >= 9 or when.hour <= 17)

        if work_time:
            # hours 9-5 on work days get higher lambda concentrated near 2.75
            poisson_lambda = random.triangular(1.5, 5, 2.75)
        elif late_night:
            # hours in middle of night get lower lambda
            poisson_lambda = random.uniform(0.0, 5.0)
        else:
            poisson_lambda = random.uniform(1.5, 4.25)

        hourly_arrivals = np.random.poisson(poisson_lambda)
        interarrival_times = np.random.exponential(
            1/poisson_lambda, size=hourly_arrivals
        )

        return hourly_arrivals, interarrival_times

    def _hack(self, when, user_list, vary_ips):
        """
        Simulate an attack by a random hacker.

        Parameters:
            - when: The datetime to start the attack.
            - user_list: The list of users to try to hack.
            - vary_ips: Whether or not to vary the IP address used for attack.

        Returns:
            The hacker's starting IP address and the end time of the attack for
            recording. When the hacker varies the IP address, the log won't record
            all the IP addresses used to simulate being unable to perfectly label
            every data point.
        """
        hacker_ip = random_ip_generator()
        random.shuffle(user_list)
        for user in user_list:
            when = self._hacker_attempts_login(
                when=when,
                source_ip=random_ip_generator() if vary_ips else hacker_ip,
                username=user
            )
        return hacker_ip, when

    def simulate(self, *, attack_prob, try_all_users_prob, vary_ips):
        """
        Simulate login attempts.

        Parameters:
            - attack_probs: The probability a hacker will attack in a given hour.
            - try_all_users_prob: The probability the hacker will try to guess
                                  the credentials for all users versus using a
                                  subset of it.
            - vary_ips: Boolean indicating whether or not to vary the IP
                        when guessing for each user. When `False`, the hacker
                        will use the same IP address for the entire attack.
        """
        hours_in_date_range = math.floor(
            (self.end - self.start).total_seconds() / 60 / 60
        )
        for offset in range(hours_in_date_range + 1):
            current = self.start + dt.timedelta(hours=offset)

            # simulate hacker
            if random.random() < attack_prob:
                attack_start = current + dt.timedelta(hours=random.random())
                source_ip, end_time = self._hack(
                    when=attack_start,
                    user_list=self.users if random.random() < try_all_users_prob \
                        else random.sample(self.users, random.randint(0, len(self.users))),
                    vary_ips=vary_ips
                )
                self.hack_log = self.hack_log.append(
                    dict(start=attack_start, end=end_time, source_ip=source_ip),
                    ignore_index=True
                )

            # simulate valid users
            hourly_arrivals, interarrival_times = self._valid_user_arrivals(current)

            random_user = random.choice(self.users)
            random_ip = random.choice(self.user_base[random_user])

            for i in range(hourly_arrivals):
                current += dt.timedelta(hours=interarrival_times[i])
                current = self._valid_user_attempts_login(current, random_user)

    @staticmethod
    def _save(data, filename, sort_column):
        """Sort a `pandas.DataFrame` by the datetime and save to a CSV file."""
        data.sort_values(sort_column).to_csv(filename, index=False)

    def save_log(self, filename):
        """Save the login attempts log to a CSV file."""
        self._save(self.log, filename, 'datetime')

    def save_hack_log(self, filename):
        """Save the record of the attacks to a CSV file."""
        self._save(self.hack_log, filename, 'start')
