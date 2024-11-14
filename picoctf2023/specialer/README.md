# `specialer`

We're dropped in a shell that looks to have nothing but `bash` installed:

    Specialer$ echo /*
    /bin /home /lib /lib64
    Specialer$ echo /bin/*
    /bin/bash

Let's enable `globstar` to help our exploration:

    Specialer$ shopt -s globstar
    Specialer$ echo ./**
    ./ ./abra ./abra/cadabra.txt ./abra/cadaniel.txt ./ala ./ala/kazam.txt ./ala/mode.txt ./sim ./sim/city.txt ./sim/salabim.txt

With that we can just list all the contents of all the local files:

    Specialer$ for f in ./**; do [ -f "$f" ] && [ -s "$f" ] && echo "$f contains: $(<"$f")"; done

That yields the file
