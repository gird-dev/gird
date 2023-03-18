include tmp/targets.mk

.cache:
	mkdir -p .cache

.cache/%: .cache
	touch $@

.PHONY: all
all: $(targets)