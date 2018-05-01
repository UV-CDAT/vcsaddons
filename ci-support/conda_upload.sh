PKG_NAME=vcsaddons
USER=cdat
VERSION="8.0"
ESMF_CHANNEL="nesii/label/dev-esmf"
echo "Trying to upload conda"
if [ `uname` == "Linux" ]; then
    OS=linux-64
    echo "Linux OS"
    yum install -y wget git gcc
    wget --no-check https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh  -O miniconda2.sh 2> /dev/null
    bash miniconda2.sh -b -p ${HOME}/miniconda2
    export PATH="$HOME/miniconda2/bin:$PATH"
    echo $PATH
    conda config --set always_yes yes --set changeps1 no
    conda config --set anaconda_upload false --set ssl_verify false
    conda install -n root -q anaconda-client conda-build
    conda install -n root gcc future
    conda update -y -q conda
    BRANCH=${TRAVIS_BRANCH}
else
    echo "Mac OS"
    OS=osx-64
    BRANCH=${CIRCLE_BRANCH}
    WORKDIR=$1
    export PATH=$WORKDIR/miniconda/bin:$PATH
fi

mkdir ~/conda-bld
conda config --set anaconda_upload no
export CONDA_BLD_PATH=${HOME}/conda-bld
echo "Cloning recipes"
git clone git://github.com/UV-CDAT/conda-recipes
cd conda-recipes
# uvcdat creates issues for build -c uvcdat confises package and channel
python ./prep_for_build.py
conda build $PKG_NAME -c cdat/label/nightly -c ${ESMF_CHANNEL} -c conda-forge -c uvcdat 
conda build $PKG_NAME -c cdat/label/nightly -c ${ESMF_CHANNEL} -c conda-forge -c uvcdat --python=3.6
anaconda -t $CONDA_UPLOAD_TOKEN upload -u $USER -l
