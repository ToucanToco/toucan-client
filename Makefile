test:
	PYTHONPATH=. pytest --cov-report term-missing --cov=toucanclient -p no:warnings tests
