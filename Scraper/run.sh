#!/bin/bash

if [ $# -gt 0 ]
then
    if [ $1 = '-pyvd' ] || [ $1 = '--pyvd' ]
    then
        echo 'Running with PyVirtualDisplay'
        python3 main.py pyvd
    elif [ $1 = '-debug' ] || [ $1 = '--debug' ]
    then
        echo 'Debug Mode ...'
        echo
        python3 main.py
    elif [ $1 = '-clean' ] || [ $1 = '--clean' ]
    then
        find . -name "*.pyc" -exec rm -rf {} \;
        echo "Cleaned ..."
    elif [ $1 = '-ins_req' ] || [ $1 = '--ins_req' ]
    then
        echo "Installing Requirements:"
        echo
        sudo apt-get -y install xvfb gtk2-engines-pixbuf
        sudo apt-get -y install xfonts-cyrillic xfonts-100dpi xfonts-75dpi xfonts-base xfonts-scalable
        sudo apt-get -y install imagemagick x11-apps
        pip3 install --requirement=../requirements.txt
    elif [ $1 = '-kill' ] || [ $1 = '--kill' ]
    then
        curl -i -H "Content-Type: application/json" -X POST -d '{"task":"KILL"}' http://localhost:2717/scraper/add_task
        echo
        echo 'Server Killed'
    elif [ $1 = '-help' ] || [ $1 = '--help' ]
    then
        echo 'Usage:'
        echo './run [option]'
        echo 
        echo 'options:'
        echo '-clean: Clean pyc files'
        echo '-ins_req: Install requirements'
        echo '-pyvd: Run using PyVirtualDisplay library'
        echo '-kill: Kill server'
        echo '-debug: Run debug mode'
    else
        echo 'Use --help for help'
    fi
else
    echo 'Running with xvfb'
    xvfb-run -a -s "-screen 0 1024x768x24" python3 main.py
fi
