#!/bin/sh

#rm -rf reports

#pybot --include $1 --outputdir reports -P lib --variable BROWSER:ff --variable ENVIRONMENT:exttest tests
pybot --include $1 --outputdir reports -P atest --variable BROWSER:ff --variable ENVIRONMENT:local atest
