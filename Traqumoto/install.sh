# Installation de Torch, d'OpenCV et de toutes les librairies puis création de l'executable

# Introduction

CYAN='\033[0;36m'
NC='\033[0m' # No Color
printf "\n${CYAN}[Install] Installation de Traqumoto${NC}\n"

# KEEP UBUNTU OR DEBIAN UP TO DATE

printf "\n${CYAN}[Install] sudo apt-get -y update${NC}\n"
sudo apt-get -y update
printf "\n${CYAN}[Install] sudo apt-get -y upgrade${NC}\n"
sudo apt-get -y upgrade
printf "\n${CYAN}[Install] sudo apt-get -y dist-upgrade${NC}\n"
sudo apt-get -y dist-upgrade
printf "\n${CYAN}[Install] sudo apt-get -y autoremove${NC}\n"
sudo apt-get -y autoremove


# INSTALL THE DEPENDENCIES

# Build tools:
printf "\n${CYAN}[Install] sudo apt-get install -y build-essential cmake${NC}\n"
sudo apt-get install -y build-essential cmake

# GUI (if you want to use GTK instead of Qt, replace 'qt5-default' with 'libgtkglext1-dev' and remove '-DWITH_QT=ON' option in CMake):
printf "\n${CYAN}[Install] sudo apt-get install -y qt5-default libvtk6-dev${NC}\n"
sudo apt-get install -y qt5-default libvtk6-dev

# Media I/O:
printf "\n${CYAN}[Install] sudo apt-get install -y zlib1g-dev libjpeg-dev libwebp-dev libpng-dev libtiff5-dev libjasper-dev libopenexr-dev libgdal-dev${NC}\n"
sudo apt-get install -y zlib1g-dev libjpeg-dev libwebp-dev libpng-dev libtiff5-dev libjasper-dev libopenexr-dev libgdal-dev

# Video I/O:
printf "\n${CYAN}[Install] sudo apt-get install -y libdc1394-22-dev libavcodec-dev libavformat-dev libswscale-dev libtheora-dev libvorbis-dev libxvidcore-dev libx264-dev yasm libopencore-amrnb-dev libopencore-amrwb-dev libv4l-dev libxine2-dev${NC}\n"
sudo apt-get install -y libdc1394-22-dev libavcodec-dev libavformat-dev libswscale-dev libtheora-dev libvorbis-dev libxvidcore-dev libx264-dev yasm libopencore-amrnb-dev libopencore-amrwb-dev libv4l-dev libxine2-dev

# Parallelism and linear algebra libraries:
printf "\n${CYAN}[Install] sudo apt-get install -y libtbb-dev libeigen3-dev${NC}\n"
sudo apt-get install -y libtbb-dev libeigen3-dev

# Python:
printf "\n${CYAN}[Install] sudo apt-get install -y python-dev python-tk python-numpy python3-dev python3-tk python3-numpy${NC}\n"
sudo apt-get install -y python-dev python-tk python-numpy python3-dev python3-tk python3-numpy

# Java:
printf "\n${CYAN}[Install] sudo apt-get install -y ant default-jdk${NC}\n"
sudo apt-get install -y ant default-jdk

# Git:
printf "\n${CYAN}[Install] sudo apt-get install -y git${NC}\n"
sudo apt-get install -y git

# Documentation:
printf "\n${CYAN}[Install] sudo apt-get install -y doxygen${NC}\n"
sudo apt-get install -y doxygen


# INSTALL Applications
printf "\n${CYAN}[Install] mkdir Applications${NC}\n"
mkdir Applications
printf "\n${CYAN}[Install] cd Applications${NC}\n"
cd Applications

# INSTALL Torch

printf "\n${CYAN}[Install] git clone https://github.com/torch/distro.git ./torch${NC}\n"
git clone https://github.com/torch/distro.git ./torch
printf "\n${CYAN}[Install] cd torch${NC}\n"
cd torch
printf "\n${CYAN}[Install] bash install-deps${NC}\n"
bash install-deps
printf "\n${CYAN}[Install] ./install.sh${NC}\n"
./install.sh
printf "\n${CYAN}[Install] cd ..${NC}\n"
cd ..

# INSTALL OpenCV 3.1.0

printf "\n${CYAN}[Install] sudo apt-get install -y unzip wget${NC}\n"
sudo apt-get install -y unzip wget
printf "\n${CYAN}[Install] wget https://github.com/opencv/opencv/archive/3.1.0.zip${NC}\n"
wget https://github.com/opencv/opencv/archive/3.1.0.zip
printf "\n${CYAN}[Install] unzip 3.1.0.zip${NC}\n"
unzip 3.1.0.zip
printf "\n${CYAN}[Install] rm 3.1.0.zip${NC}\n"
rm 3.1.0.zip
printf "\n${CYAN}[Install] mv opencv-3.1.0 OpenCV${NC}\n"
mv opencv-3.1.0 OpenCV
printf "\n${CYAN}[Install] cd OpenCV${NC}\n"
cd OpenCV
printf "\n${CYAN}[Install] mkdir build${NC}\n"
mkdir build
printf "\n${CYAN}[Install] cd build${NC}\n"
cd build
printf "\n${CYAN}[Install] cmake -DWITH_QT=ON -DWITH_OPENGL=ON -DFORCE_VTK=ON -DWITH_TBB=ON -DWITH_GDAL=ON -DWITH_XINE=ON -DBUILD_EXAMPLES=ON ..${NC}\n"
cmake -DWITH_QT=ON -DWITH_OPENGL=ON -DFORCE_VTK=ON -DWITH_TBB=ON -DWITH_GDAL=ON -DWITH_XINE=ON -DBUILD_EXAMPLES=ON ..
printf "\n${CYAN}[Install] make -j4${NC}\n"
make -j4
printf "\n${CYAN}[Install] sudo make install${NC}\n"
sudo make install
printf "\n${CYAN}[Install] cd ..${NC}\n"
cd ..
printf "\n${CYAN}[Install] cd ..${NC}\n"
cd ..

# INSTALL Luarocks
printf "\n${CYAN}[Install] sudo apt-get install luarocks${NC}\n"
sudo apt-get -y install luarocks

# LINK Torch & OpenCV

printf "\n${CYAN}[Install] git clone https://github.com/VisionLabs/torch-opencv.git${NC}\n"
git clone https://github.com/VisionLabs/torch-opencv.git
printf "\n${CYAN}[Install] cd torch-opencv${NC}\n"
cd torch-opencv
printf "\n${CYAN}[Install] luarocks make cv-scm-1.rockspec${NC}\n"
luarocks make cv-scm-1.rockspec
printf "\n${CYAN}[Install] source ~/.bashrc${NC}\n"
source ~/.bashrc
printf "\n${CYAN}[Install] cd ..${NC}\n"
cd ..

# INSTALL Luastatic
printf "\n${CYAN}[Install] git clone https://github.com/ers35/luastatic${NC}\n"
git clone https://github.com/ers35/luastatic

printf "\n${CYAN}[Install] cd ..${NC}\n"
cd ..


# Création de l'exécutable
printf "make"
make
