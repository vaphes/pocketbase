rm .cov_annotate/*.py,cover
pytest -vs --cov=pocketbase  --cov-report annotate:.cov_annotate tests/${1}
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics