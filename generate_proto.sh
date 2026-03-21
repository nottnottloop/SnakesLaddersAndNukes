#!/bin/bash

protoc --python_out=. --pyi_out=. ./src/shared/game.proto
