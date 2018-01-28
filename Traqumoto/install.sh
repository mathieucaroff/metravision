# Installation de Torch, d'OpenCV et de toutes les librairies puis création de l'executable


### HEADER ###
CYAN='\033[0;36m'
NC='\033[0m' # No Color
function echolor () {
    echo "${CYAN}$@${NC}\n"
}

function echoexe () {
    echolor "[Install] $*"
    "$@"
}



###  BODY  ###

echolor "Installation de Traqumoto"

# Updates
echoexe sudo apt-get -y update
echoexe sudo apt-get -y upgrade
echoexe sudo apt-get -y dist-upgrade
echoexe sudo apt-get -y autoremove


# INSTALL THE DEPENDENCIES

# Build tools:
echoexe sudo apt-get install -y build-essential cmake

# GUI (if you want to use GTK instead of Qt, replace 'qt5-default' with 'libgtkglext1-dev' and remove '-DWITH_QT=ON' option in CMake):
echoexe sudo apt-get install -y qt5-default libvtk6-dev

# Media I/O:
echoexe sudo apt-get install -y zlib1g-dev libjpeg-dev libwebp-dev libpng-dev libtiff5-dev libjasper-dev libopenexr-dev libgdal-dev

# Video I/O:
echoexe sudo apt-get install -y libdc1394-22-dev libavcodec-dev libavformat-dev libswscale-dev libtheora-dev libvorbis-dev libxvidcore-dev libx264-dev yasm libopencore-amrnb-dev libopencore-amrwb-dev libv4l-dev libxine2-dev

# Parallelism and linear algebra libraries:
echoexe sudo apt-get install -y libtbb-dev libeigen3-dev

# Python:
echoexe sudo apt-get install -y python-dev python-tk python-numpy python3-dev python3-tk python3-numpy

# Java:
echoexe sudo apt-get install -y ant default-jdk

# Git:
echoexe sudo apt-get install -y git

# Documentation:
echoexe sudo apt-get install -y doxygen


# INSTALL Applications
echoexe mkdir Applications
echoexe cd Applications

# INSTALL Torch

echoexe git clone https://github.com/torch/distro.git ./torch
echoexe cd torch
echoexe bash install-deps
echoexe ./install.sh
echoexe cd ..

# INSTALL OpenCV 3.1.0

echoexe sudo apt-get install -y unzip wget
echoexe wget https://github.com/opencv/opencv/archive/3.1.0.zip
echoexe unzip 3.1.0.zip
# echoexe rm 3.1.0.zip
echoexe mv opencv-3.1.0 OpenCV
echoexe cd OpenCV
echoexe mkdir build
echoexe cd build
echoexe cmake -DWITH_QT=ON -DWITH_OPENGL=ON -DFORCE_VTK=ON -DWITH_TBB=ON -DWITH_GDAL=ON -DWITH_XINE=ON -DBUILD_EXAMPLES=ON ..
echoexe make -j4
echoexe sudo make install
echoexe pwd
echoexe cd ../..

# INSTALL Luarocks
echoexe sudo apt-get -y install luarocks

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