.PHONY: install eval eval-offline test
install:
	pip install -r requirements.txt

# Uses Gemini if GEMINI_API_KEY is set, otherwise the offline backend. Dev split only.
eval:
	python eval.py --split dev

eval-offline:
	python eval.py --split dev --backend offline --tag m2-baseline

test:
	python -m pytest -q
