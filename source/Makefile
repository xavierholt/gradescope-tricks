.PHONY: ../grader.zip clean

../grader.zip:
	rm  -f $@
	zip -r $@ autograder.py run_autograder setup.sh code tests tests.py

clean:
	rm  -f ../grader.zip
