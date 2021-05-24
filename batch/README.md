# Batch at SLAC
This directory contains the basic files you need to submit batch jobs to SLAC through the bsub system.
In order to run batch jobs, there is a series of set-up steps that are necessary.

## Custom Production Image
If you need developments of `ldmx-sw` or `ldmx-analysis` installed in the container,
then you should look at [this page about making your own production image](https://ldmx-software.github.io/docs/custom-production-image.html).

If you just want to run a specific configuration of a release of `ldmx-sw`, then just make sure you have a copy of the image you want to use somewhere you have access at SLAC. (_Hint_: These images end in `.sif`. If you can't find the right one you can download one with \
`source ldmx-sw/script/ldmx-env.sh; ldmx-container-pull pro <ldmx-sw-version>`).

## Config Script

The file you need to worry about editing to your specifc job is `config.py`.
The `config.py` file given here shows the execution of the most basic simulation we have and shows the three inputs given to the python script automatically by the submission script.
These three inputs (the argparse stuff at the top) is _necessary_ to be able to run your script.

Input | Description
---|---
`input_file` | If an input file for the run is given, this argument is set to the name of the input file after it is copied over to the working directory.
`batch_job` | Set to the bsub job ID number
`run_number` | Passed as the run number from the `ldmx_bsub.py` script. Look there if you wish to control how these run numbers are generated.

You can feel free to add other arguments here as well, but since these three arguments need to interact with the other parts of the batch machinery, they are _required_.

## Test the Config Script
Make sure to test the configuration script by running it yourself using the production image you want to run with. You can do so by running the `singularity` command directly.
```
singularity run \
  --no-home \
    --bind $(pwd) \
      <full-path-to-.sif-file> \
        . \
	  your_config.py \
	    <any-config-args>
	    ```

## Test the Working Script
The `run_fire.sh` bash script is what actually runs the job on the working computer and then copies the resulting files back to your chosen output directory. Double check that this works by simply running it in your local environment.
```
bash run_fire.sh  <full-path-to-.sif-file> <full-path-to-config.py> $(pwd) "--run_number 0 --batch_job 0 <any-other-args>" <optional-full-path-to-input-file>
```

## The Submission Script
The `ldmx_bsub.py` script submits the working script to the batch system as the "jobs" that need to be run. It has a more complex interface so that it can handle production jobs that don't require any input files and recon/analysis jobs that do. Use `python ldmx_bsub.py --help` to get a full list of options. The two most basic running modes are given below.

### Production (no input files)
`python ldmx_bsub.py -c your_config.py -s your_image.sif -o output/directory --num_jobs 100`
This will run `your_config.py` inside `your_image.sif`, copying the output to `output/directory` one hundred times using a sequential count as the run numbers.

### Analysis (input files)
`python ldmx_bsub.py -c your_config.py -s your_image.sif -o output/directory --input_dir directory/with/only/input/files`
This will run `your_config.py` inside `your_image.sif` passing the files in `directory/with/only/input/files` one at a time to the config with `--input_file the_file`. Any output files are then copied to `output/directory`.