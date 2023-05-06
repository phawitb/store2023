#copy to ../store2023

sleep 10

DIR="store2023"
if [ -d "$DIR" ]; then
  ### Take action if $DIR exists ###
  echo "1exist ${DIR}"

else
  ###  Control will jump here if $DIR does NOT exists ###
  echo "1not exist floder ${DIR}"
  # exit 1
fi

if [[ "$(ping -c 1 8.8.8.8 | grep '100% packet loss' )" != "" ]]; then
    echo "Internet isn't present"
    exit 1
else
    echo "Internet is present"
    # wget www.site.com

    DIR="store2023"
    if [ -d "$DIR" ]; then
        ### Take action if $DIR exists ###
        echo "exist ${DIR}"
        
        rm -rf store2023
        echo "remove ${DIR}"

    else
        ###  Control will jump here if $DIR does NOT exists ###
        echo "not exist floder ${DIR}"
        # exit 1
    fi

    git clone https://github.com/phawitb/store2023.git

    sleep 5

    cd store2023 && bash run.sh

fi
