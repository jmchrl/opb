#!/bin/sh

# BASEDIR chemin absolu vers l'application opb
BASEDIR="$(which $0)"
BASEDIR=${BASEDIR%/*}


cd $BASEDIR
/usr/bin/python3 $BASEDIR/opb.py
cd -
