# Maitrise
---
## Data

**540_tests_limo** contains the following:
- 540 bag files with different manoeuvers under different circumstances with the limo car. (Some of these bags might be discarded in **weird bags** folder if something went wrong with the test eg: at least one important topic is missing, trajectory is too bumpy, etc. These bags will not be used for training in the learning phase.)
- The excel file `limo_tests.xlsx` containing the description of all 540 tests (what is the manoeuver and under what circumstances + specs of car used).
- `all_path_same_plot.py` code that plots all trajectories of the bag files in the current folder on the same plot.
- `different_plot.py` code that plots all trajectories of the bag files in the current folder on different plots. (**WARNING: This code will create 500+ pop-up plots)**
- `EndPoint_excel.py` code that will copy everything in the `limo_tests.xlsx` and add the ending point of the trajectory to it in another Excel file. The ending position and orientation of the vehicle according to the manoeuver and circumstance around that manoeuver will be used later in the learning phase.
- **stats** folder containing 9 batches of approximately 10 bag files doing the same exact manoeuver in the same environment. The goal here is to determine how repeatable is the outcome of these tests. The `plot&stats.py` code plots all 10 trajectories of a batch on a same plot and gives a report on how repeatable is the outcome.

**540_tests_racecar** contains the following:
- 540 bag files with different manoeuvers under different circumstances with the racecar. (Some of these bags might be discarded in **weird bags** folder if something went wrong with the test eg: at least one important topic is missing, trajectory is too bumpy, etc. These bags will not be used for training in the learning phase.)
- The excel file `racecar_tests.xlsx` containing the description of all 540 tests (what is the manoeuver and under what circumstances + specs of car used).
- `all_path_same_plot.py` code that plots all trajectories of the bag files in the current folder on the same plot.
- `different_plot.py` code that plots all trajectories of the bag files in the current folder on different plots. (**WARNING: This code will create 500+ pop-up plots)**
- `EndPoint_excel.py` code that will copy everything in the `racecar_tests.xlsx` and add the ending point of the trajectory to it in another Excel file. The ending position and orientation of the vehicle according to the manoeuver and circumstance around that manoeuvre will be used later in the learning phase.
- **stats** folder containing 9 batches of approximately 10 bag files doing the same exact manoeuver in the same environment. The goal here is to determine how repeatable is the outcome of these tests. The `plot&stats.py` code plots all 10 trajectories of a batch on a same plot and gives a report on how repeatable is the outcome.

**540_tests_Xmaxx** contains the following:
- 540 bag files with different manoeuvers under different circumstances with the Xmaxx car. (Some of these bags might be discarded in **weird bags** folder if something went wrong with the test eg: at least one important topic is missing, trajectory is too bumpy, etc. These bags will not be used for training in the learning phase.)
- The excel file `Xmaxx_tests.xlsx` containing the description of all 540 tests (what is the manoeuver and under what circumstances + specs of car used).
- `all_path_same_plot.py` code that plots all trajectories of the bag files in the current folder on the same plot.
- `different_plot.py` code that plots all trajectories of the bag files in the current folder on different plots. (**WARNING: This code will create 500+ pop-up plots)**
- `EndPoint_excel.py` code that will copy everything in the `Xmaxx_tests.xlsx` and add the ending point of the trajectory to it in another Excel file. The ending position and orientation of the vehicle according to the manoeuver and circumstance around that manoeuvre will be used later in the learning phase.

---
## Learning

**excel_data**

---
## Simulation

- `create_sim_database.py` code creates a database in an Excel file with 16 500 points with different combinations of manoeuvers and environments with their simulated outcome using a dynamic bicycle simulator. The excel file is saved in the **sim_database** folder.
- `plot_sim.py` code can plot the simulated trajectory of a specific car doing a specific manoeuver in a given environment.

## Images

This folder contains the images used in this README file.
