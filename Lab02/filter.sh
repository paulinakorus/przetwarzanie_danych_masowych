#!/usr/bin/env bash

# Filtrowanie strumienia: znaki alfanumeryczne, spacja, nowa linia oraz myślnik na końcu
tr -cd '[:alnum:] \n-' < /dev/urandom