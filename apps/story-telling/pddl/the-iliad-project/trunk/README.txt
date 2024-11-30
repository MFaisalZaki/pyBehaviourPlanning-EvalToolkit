The PDDL code developed for the project complies with PDDL 2.1 and was tested with the SGPlan 6 planner.

To download the latest version of the SGPlan planner, check the following link:

http://ipc.informatik.uni-freiburg.de/Planners?action=AttachFile&do=get&target=seq-sat-sgplan6x.tar.bz2

To run the SGPlan planner, you need a machine with Linux Ubuntu and a copy of Bison and Flex installed on it.

To install the latest version of Flex and Bison, you can do the following steps:

Open a terminal: press <CTRL> + <Alt> + <T>.
Type the following commands:

sudo apt-get update 
sudo apt-get upgrade 
sudo apt-get install flex bison

To test the PDDL files domain and problem concerning the first book of the Iliad with SGPlan, do the following steps:

- Create a new folder into the main SGPlan folder, and call it 'Iliad';
- Copy the PDDL files into the 'Iliad' folder;
- Open a terminal: press <CTRL> + <Alt> + <T>;
- Go into the main SGPlan folder;
- Type the following command: ./sgplan -o Iliad/iliad-domain.pddl -f Iliad/iliad-problem-first-book.pddl