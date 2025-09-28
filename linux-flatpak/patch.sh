#!/bin/bash

while getopts v:i:s: flag
do
    case "${flag}" in
        v) version=${OPTARG};;
        i) id=${OPTARG};;
        s) hash=${OPTARG};;
    esac
done

date=$(date '+%Y-%m-%d')

sed -i s/{VERSION}/$version/g com.tercad.tlum.yml
sed -i s/{SHA256}/$hash/g com.tercad.tlum.yml

sed -i s/{VERSION}/$version/g com.tercad.tlum.metainfo.xml
sed -i s/{DATE}/$date/g com.tercad.tlum.metainfo.xml
