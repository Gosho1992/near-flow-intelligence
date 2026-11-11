PY ?= python3
.PHONY: data refresh test docs serve site verify-prediction

data:            ## rebuild every output offline from data/raw + data/work
	NFI_OFFLINE=1 $(PY) -m nfi.build
	$(PY) -m nfi.docs
	$(MAKE) site

refresh:         ## re-fetch chain data up to today (network), then rebuild
	$(PY) -m nfi.refresh
	$(MAKE) data

test:            ## 10 independent checks (offline)
	NFI_OFFLINE=1 $(PY) -m unittest discover -s tests -v

docs:
	$(PY) -m nfi.docs

site:            ## copy outputs next to the dashboard
	mkdir -p site/data && cp data/out/*.json data/out/*.csv site/data/

serve: site
	cd site && $(PY) -m http.server 8000

verify-prediction:
	NFI_OFFLINE=1 $(PY) -m nfi.prediction
