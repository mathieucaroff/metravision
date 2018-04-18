#!/bin/bash
# Installation de Torch, d'OpenCV et de toutes les librairies puis création de l'executable


### HEADER ###
CYAN='\033[0;36m'
NC='\033[0m' # No Color

function echolor () {
    echo -e "${CYAN}$@${NC}\n"
}

function echoexe () {
    echolor "[TRM][Install] $*"
    "$@"
}

function echoexe-apty () {
    echoexe sudo apt-get install -y "$@"
}


APT_PACKAGE_LIST=(build-essential cmake qt5-default libvtk6-dev zlib1g-dev libjpeg-dev libwebp-dev libpng-dev libtiff5-dev libopenexr-dev libgdal-dev libjasper-dev libdc1394-22-dev libavcodec-dev libavformat-dev libswscale-dev libtheora-dev libvorbis-dev libxvidcore-dev libx264-dev yasm libopencore-amrnb-dev libopencore-amrwb-dev libv4l-dev libxine2-dev libtbb-dev libeigen3-dev python-dev python-tk python-numpy python3-dev python3-tk python3-numpy ant default-jdk git doxygen unzip wget luarocks)


###  BODY  ###

echolor "[TRM] Installation de Traqumoto"

# Updates
echoexe sudo apt-get update -y
echoexe sudo apt-get upgrade -y
echoexe sudo apt-get dist-upgrade -y
echoexe sudo apt-get autoremove -y


# INSTALL THE DEPENDENCIES

## All of them at once
echoexe-apty "${APT_PACKAGE_LIST[@]}"
echoexe-apty "${APT_PACKAGE_LIST[@]}" # I'm not sure why I do it twice, but it seems more secure

# Build tools:
echoexe-apty build-essential cmake

# GUI (if you want to use GTK instead of Qt, replace 'qt5-default' with 'libgtkglext1-dev' and remove '-DWITH_QT=ON' option in CMake):
echoexe-apty qt5-default libvtk6-dev

# Media I/O:
echoexe-apty zlib1g-dev libjpeg-dev libwebp-dev libpng-dev libtiff5-dev libopenexr-dev libgdal-dev
echoexe-apty libjasper-dev
echolor "libjasper-dev has been removed from debian (unmaintained). It's unsure wheather it is needed."

# Video I/O:
echoexe-apty libdc1394-22-dev libavcodec-dev libavformat-dev libswscale-dev libtheora-dev libvorbis-dev libxvidcore-dev libx264-dev yasm libopencore-amrnb-dev libopencore-amrwb-dev libv4l-dev libxine2-dev

# Parallelism and linear algebra libraries:
echoexe-apty libtbb-dev libeigen3-dev

# Python:
echoexe-apty python-dev python-tk python-numpy python3-dev python3-tk python3-numpy

# Java:
echoexe-apty ant default-jdk

# Git:
echoexe-apty git

# Documentation:
echoexe-apty doxygen


# INSTALL Applications
echoexe mkdir -p Applications
echoexe cd Applications

# INSTALL Torch
echoexe git clone https://github.com/torch/distro.git ./torch
echoexe cd torch
echoexe bash install-deps
echo y | echoexe ./install.sh
echoexe cd ..

# INSTALL OpenCV 3.1.0
echoexe-apty unzip wget
echoexe wget https://github.com/opencv/opencv/archive/3.1.0.zip
echoexe unzip 3.1.0.zip
# echoexe rm 3.1.0.zip
echoexe mv opencv-3.1.0 OpenCV
echoexe cd OpenCV
echoexe mkdir -p build
echoexe cd build
echoexe cmake -DWITH_QT=ON -DWITH_OPENGL=ON -DFORCE_VTK=ON -DWITH_TBB=ON -DWITH_GDAL=ON -DWITH_XINE=ON -DBUILD_EXAMPLES=ON ..
echoexe make -j4
echoexe sudo make install
echoexe pwd
echoexe cd ../..

# INSTALL Luarocks
echoexe-apty luarocks

# LINK Torch & OpenCV
echoexe git clone https://github.com/VisionLabs/torch-opencv.git
echoexe cd torch-opencv
echoexe luarocks make cv-scm-1.rockspec
echoexe source ~/.bashrc
echoexe cd ..

# INSTALL Luastatic
echoexe git clone https://github.com/ers35/luastatic
echoexe cd ..

# Création de l'exécutable
echoexe make
