#!/bin/sh

rsync -avh nomad-synthesis-plugin/ .
rm -rfv nomad-synthesis-plugin
