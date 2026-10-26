#!/bin/bash

while getopts v:i: flag
do
    case "${flag}" in
        v) version=${OPTARG};;
        i) commit=${OPTARG};;
    esac
done

if ! grep -q "<release version=\"$version\"" com.tercad.tlum.metainfo.xml; then
    echo "Release $version is missing in com.tercad.tlum.metainfo.xml" >&2
    exit 1
fi

sed -i s/{VERSION}/$version/g com.tercad.tlum.yml
sed -i s/{COMMIT}/$commit/g com.tercad.tlum.yml
