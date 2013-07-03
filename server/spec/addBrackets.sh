#/bin/bash

# cat somefile | xargs -d'\n' -L 1 ./addBrackets.sh > otherfile.py

code=`echo $1 | cut -f 1 -d' '`
lang=`echo $1 | cut -f 2-10 -d' '`
echo '    '\(\'$code\', \'$lang\'\),
