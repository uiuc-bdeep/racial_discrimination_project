all: main
.PHONY: all

main: step_1_get_survey.R mergeData_GA.py
	rm -rf "/individual joins"*
	rm -rf "/individual timestamp files"*
	Rscript step_1_get_survey.R
	python3 mergeData_GA.py
	rm -rf "/individual joins"*
	rm -rf "/individual timestamp files"*

clean:
	rm -f *.pyc
	clear
	clear
