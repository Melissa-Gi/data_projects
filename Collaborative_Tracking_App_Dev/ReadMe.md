PLEASE FIND GITLAB REPO HERE: https://gitlab.cs.uct.ac.za/capstone_cs3/TeamTJM.git

This application is configured to run in a Python virtual environment for your convenience:

1. Create the virtual environment in TeamTJM directory

python3 -m venv venv
NB. This application has currently been tested to success with 3.8.3 and 3.10.12

2. Activate the virutal environment:

source venv/bin/activate (linux/macOS)
venv/Scripts/Activate.ps1 (PowerShell in Windows)

3. Install the needed packages:

pip install -r requirements.txt 
Again, you only need to do this once.

4. Run the application
Run the application file App.py from within the TeamTJM directory

cd TeamTJM
App/App.py

5. Running the testing scripts:

Navigate to the TeamTJM directory (if not already) and run the command corresponding to the functionality you wish to test. Unit, intergration, end-to-end tests, and more are included in each testing script. Each test will produce a testing report in the terminal.

A. Object Tracking  python Test_Scripts/TrackingTests.py -v
B. Object Manager   python Test_Scripts/ObjectManagerTests.py -v

6. At the end of the session, deativate the python virtual environment

deactivate