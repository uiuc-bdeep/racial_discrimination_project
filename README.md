# Racial Discrimination Project
## Environment Setup
### Specify Project Root
Set your PROJ_ROOT environment variable and navigate to your PROJ_ROOT

	export PROJ_ROOT="/path/to/racial_discrimination_project"
	cd $PROJ_ROOT

### Clone Project
If git is configured from the command line:

	git clone git@github.com:uiuc-bdeep/racial_discrimination_project.git

or if using a local copy:

	git clone https://github.com/uiuc-bdeep/racial_discrimination_project.git

### Create Virtual Environment

Project is currently using Python2

Specify a virtualenv that with python2:
	virtualenv env -p /usr/bin/python2

Activate it with:
	source env/bin/activate
