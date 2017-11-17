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
