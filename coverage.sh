rm .cov_annotate/*.py,cover
pytest -s --cov=pocketbase  --cov-report annotate:.cov_annotate tests/
