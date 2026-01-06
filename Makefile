# Makefile (for those who prefer make over just)
# This is a simple wrapper around justfile

.PHONY: help setup install dev test lint fmt check clean

help:
	@just --list

setup:
	@just setup

install:
	@just install

dev:
	@just dev

test:
	@just test

lint:
	@just lint

fmt:
	@just fmt

check:
	@just check

clean:
	@just clean

# Forward any unknown target to just
%:
	@just $@

