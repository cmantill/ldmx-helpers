#!/bin/bash

set -ex

###############################################################################
# run_fire.sh
#   Batch running script for executing fire on a worker node and then copying
#   the results to an output directory.
###############################################################################

_singularity_img=$1 #container image to use to run
_config_script=$2 #script itself to run
_output_dir=$3 #output directory to copy products to
_config_args=$4 #arguments to configuration script
_input_file=$5 #optional

if ! cd /scratch/ 
then
  echo "Using the scratch area in the ldmx group area."
  cd /nfs/slac/g/ldmx/production/scratch/
fi

if ! mkdir -p $USER
then
  echo "Don't have access to the scratch area!"
  exit 111
fi
cd $USER

_batch_job_id=$LSB_JOBID
if [[ -z $_batch_job_id ]]
then
  _batch_job_id=1
fi

_config_args="$_config_args --batch_job $_batch_job_id"

mkdir -p $_batch_job_id
cd $_batch_job_id

if [[ ! -z "$(ls -A .)" ]]
then
  # temp directory non-empty
  #   we need to clean it before running so that
  #   the only files are the ones we know about
  rm -r *
fi

if [[ ! -z $_input_file ]]
then
  cp $_input_file .
  _input_file=$(basename $_input_file)
  _config_args="$_config_args --input_file $_input_file"
fi

cp $_config_script .
_config_script=$(basename $_config_script)

singularity run \
  --no-home \
  --bind $(pwd) \
  --cleanenv \
  $_singularity_img \
  $(pwd) \
  $_config_script \
  $_config_args

# first remove the input files
#   so they don't get copied to the output
rm -r __pycache__ $_config_script $_input_file

# copy all other generated root files to output
cp *.root $_output_dir
