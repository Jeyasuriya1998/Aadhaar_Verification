#!/bin/bash
echo "Do you want to configure the Global User and Email ?"
select yn in "Yes" "No"; do 
    case $yn in
        Yes ) echo "Do something"; 
                echo "Enter Your name : "
                read name
                echo "Entered Name : $name"; 
                git config --global user.name "$name"
                echo "Enter Your Email : "
                read Email
                echo "Entered Email : $Email"; 
                git config --global user.email "$Email"
                break;;
        No ) break;;
    esac
done

echo "Do you want to Clone Any Url ?"
select yn in "Yes" "No"; do 
    case $yn in
        Yes ) echo "Do something"; 
                echo "Enter Your URL : "
                read URL
                echo "Entered Name : $URL"; 
                git clone $URL
                break;;
        No ) break;;
    esac
done

