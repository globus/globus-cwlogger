from setuptools import setup, find_packages

setup(
    name="globus_cw_loghandler",
    version='0.1.0',
    packages=find_packages(),

    # descriptive info, non-critical
    description="Python logging.SocketHandler customized for use with Globus CWLogger daemon.",
    url="https://github.com/globus/globus-cwlogger",
)
