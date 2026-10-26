#!/bin/bash

while getopts v:i: flag
do
    case "${flag}" in
        v) version=${OPTARG};;
        i) commit=${OPTARG};;
    esac
done

date=$(date '+%Y-%m-%d')

sed -i s/{VERSION}/$version/g com.tercad.tlum.yml
sed -i s/{COMMIT}/$commit/g com.tercad.tlum.yml

sed -i s/{VERSION}/$version/g com.tercad.tlum.metainfo.xml
sed -i s/{DATE}/$date/g com.tercad.tlum.metainfo.xml
sed -i "s|{CHANGE}|The list of changes is available on the release page|g" com.tercad.tlum.metainfo.xml
