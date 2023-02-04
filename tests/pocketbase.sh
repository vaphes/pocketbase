#!/bin/bash
#get latest release version number
cd `mktemp -d`
release=$(curl -IkLs -o /dev/null -w %{url_effective} https://github.com/pocketbase/pocketbase/releases/latest|grep -o "[^/]*$"| sed "s/v//g")
echo ${release}
wget -qO- https://github.com/pocketbase/pocketbase/releases/download/v${release}/pocketbase_${release}_linux_amd64.zip | bsdtar -xvf- --include pocketbase -C .
chmod 755 ./pocketbase
./pocketbase serve
