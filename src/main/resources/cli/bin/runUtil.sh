#
# Copyright 2017 XEBIALABS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

#!/bin/bash
: "${XLR_HOME:?must me set to the base location of the XL Release Server.}"
: "${1:?Command takes one argument, you must specify the script to execute.}"

for i in $( ls ${XLR_HOME}/lib/*.jar ); do
    if [ -z "${python_path}" ]; then
        python_path="${i}"
    else
        python_path="${python_path}:${i}"
    fi
done

jython_standalone_jar=$(ls ${XLR_HOME}/lib/jython-standalone*.jar)

if [ "${1}" == "shell" ]; then
    java -Dpython.path=${python_path} -jar ${jython_standalone_jar}
else
    java -Dpython.path=${python_path} -jar ${jython_standalone_jar} ${1}
fi
