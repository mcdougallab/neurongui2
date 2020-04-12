Install via:

    python setup.py install


Notes:

    "import neurongui2" should be at the beginning of your script; any actions before
    that line will be run twice when launching the script as a stand-alone. (This issue
    does not arise when using "python -m neurongui2 filename.py" or launching the
    script from inside neurongui2.)

Files:

neurongui2/__init__.py: The main python script to run; initalizes with shell
neurongui2/main_script.html: wrapper html file with all JS code for various elements
simulation1.html: window with html elements designed to control and plot a simple simulation
simulation_setup.py, gui_test*: short user test scripts
neurongui2/gui.py: for initial test rerouting
neurongui2/html, neurongui2/js: html and js libraries

# old TODO: certain errors cause NEURON to shutdown... some of these don't need to, e.g. ca with unspecified charge in a species declaration
