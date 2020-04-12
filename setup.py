import setuptools

with open('requirements.txt') as f:
    requirements = [item for item in f.read().splitlines() if not item.startswith('#')]

setuptools.setup(
    name="neurongui2",
    version="0.0.1",
    author="RA McDougal and L Eggleston",
    author_email="robert.mcdougal@yale.edu",
    description="An alternative GUI for NEURON; full functionality needs NEURON 7.8+",
    url="https://github.com/ramcdougal/neurongui2",
    install_requires=requirements,
    packages=['neurongui2'],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)