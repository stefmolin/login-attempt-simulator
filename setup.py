from distutils.core import setup

setup(
    name='log_in_attempt_simulator',
    version='0.1',
    description='Simulate log in attempts from valid users and hackers.',
    author='Stefanie Molin',
    author_email='24376333+stefmolin@users.noreply.github.com',
    license='MIT',
    url='https://github.com/stefmolin/log-in-attempt-simulator',
    packages=['log_in_attempt_simulator'],
    install_requires=[
        'numpy>=1.15.2',
        'pandas>=0.23.4'
    ],
)
