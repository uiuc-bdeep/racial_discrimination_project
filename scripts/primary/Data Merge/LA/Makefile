all: main
.PHONY: all

main: step_1_get_survey.R mergeData_LA.py
	Rscript step_1_get_survey.R
	python3 mergeData_LA.py

clean:
	rm -f *.pyc
	clear
	clear
