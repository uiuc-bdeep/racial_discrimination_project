all: main
.PHONY: all

main: step_1_get_survey.R mergeData_GA.py
	clear
	clear
	rm -f "individual joins"/*
	rm -f "individual timestamp files"/*
	rm -f "input/Trulia.csv"
	rm -f "input/responses_concatenated.csv"
	rm -f "output/GA_Trulia_MERGED_allTimestamps_MERGED_allResponses.csv"
	Rscript step_1_get_survey.R
	python3 mergeData_GA.py

clean:
	rm -f *.pyc
	clear
	clear
