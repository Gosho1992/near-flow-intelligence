PY ?= python3
.PHONY: data rebuild refresh test docs serve site verify-prediction

# Build published outputs from already collected data/work snapshots (offline).
data:            ## rebuild headline, docs and site from data/work
	NFI_OFFLINE=1 $(PY) -m nfi.build
	$(PY) -m nfi.docs
	$(MAKE) site

# Rebuild the working datasets from committed raw API responses (offline).
# This is the full raw -> work -> out path; it never makes a mainnet transaction.
rebuild:         ## rebuild all datasets offline from data/raw
	NFI_OFFLINE=1 $(PY) -m nfi.attribution
	NFI_OFFLINE=1 $(PY) -m nfi.collect_chain
	NFI_OFFLINE=1 $(PY) -m nfi.collect_custody
	NFI_OFFLINE=1 $(PY) -m nfi.institutional
	NFI_OFFLINE=1 $(PY) -m nfi.protocol
	NFI_OFFLINE=1 $(PY) -m nfi.sec_check
	$(MAKE) data

refresh:         ## re-fetch chain data up to today (network), then rebuild
	$(PY) -m nfi.refresh
	$(MAKE) data

test:            ## run offline unit and invariant checks
	NFI_OFFLINE=1 $(PY) -m unittest discover -s tests -v

docs:
	$(PY) -m nfi.docs

site:            ## copy outputs next to the dashboard
	mkdir -p site/data && cp data/out/*.json data/out/*.csv site/data/

serve: site
	cd site && $(PY) -m http.server 8000

verify-prediction:
	NFI_OFFLINE=1 $(PY) -m nfi.prediction
	NFI_OFFLINE=1 $(PY) -m nfi.prediction2
	NFI_OFFLINE=1 $(PY) -m nfi.signposts
