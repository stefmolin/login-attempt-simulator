from distutils.core import setup

setup(
    name='login_attempt_simulator',
    version='0.1',
    description='Simulate login attempts from valid users and hackers.',
    author='Stefanie Molin',
    author_email='24376333+stefmolin@users.noreply.github.com',
    license='MIT',
    url='https://github.com/stefmolin/login-attempt-simulator',
    packages=['login_attempt_simulator'],
    install_requires=[
        'numpy>=1.15.2',
        'pandas>=0.23.4'
    ],
)
