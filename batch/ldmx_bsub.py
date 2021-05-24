#!/usr/bin/env python

import time
import argparse
import os, sys
import subprocess

# Parse command line arguments
parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

# required args
parser.add_argument("-c","--config",required=True,type=str,help="Config script to run.")
parser.add_argument("-s","--singularity_img",required=True,type=str,help="Image to run configuration inside of.")
parser.add_argument("-o","--out_dir",required=True,type=str,help="Directory to copy output to.")

# optional args
parser.add_argument("--input_dir",default=None,type=str,help="Directory containing input files to run over.")
parser.add_argument("--num_jobs",type=int,default=None,help="Number of jobs to run (if not input directory given).")
parser.add_argument("--config_args",type=str,default='',help="Extra arguments to be passed to the configuration script.")
parser.add_argument("--start_job",type=int,default=0,help="Starting number to use when counting jobs (and run numbers)")

# rarely-used optional args
parser.add_argument("-t","--test",action='store_true',dest='test',help="Don't submit the job to the batch.")
parser.add_argument("--run_script",type=str,help="Script to run jobs on worker nodes with.",default='%s/run_fire.sh'%os.path.dirname(os.path.realpath(__file__)))
parser.add_argument("--batch_cmd",type=str,help="Command to use to submit a single job to batch.",default="bsub -R 'select[centos7]' -m 'kisofarm' -q medium -W 2800")

args = parser.parse_args()

jobs = 0

if args.input_dir is not None :
    full_input_dir = os.path.realpath(args.input_dir)
    inputFileList = os.listdir(args.input_dir)
    if args.num_jobs is not None :
        jobs = min(args.num_jobs,len(inputFileList))
    else :
        jobs = len(inputFileList)
elif args.num_jobs is not None :
    jobs = args.num_jobs
else :
    parser.error("Either an input directory of files or a number of jobs needs to be given.")

# working script requires full paths so we get them here
config = os.path.realpath(args.config)
out_dir = os.path.realpath(args.out_dir)
run_script = os.path.realpath(args.run_script)
singularity_img = os.path.realpath(args.singularity_img)

# Turn off emailing about jobs
email_command = ['bash', '-c', 'export LSB_JOB_REPORT_MAIL=N && env']
proc = subprocess.Popen(email_command,stdout=subprocess.PIPE,encoding='utf8')

for line in proc.stdout: 
    (key, _, value) = line.partition('=')
    os.environ[key] = value.strip()

proc.communicate()

# Write the command to submit to the batch system, this includes everything except the per-job changes
command = "bash %s %s %s %s"%(os.path.realpath(args.run_script),
        os.path.realpath(args.singularity_img),
        os.path.realpath(args.config),
        os.path.realpath(args.out_dir))

# Actually start submitting jobs
for job in range(args.start_job,args.start_job+jobs):

    # wait until the number of jobs pending is <= 10
    if not args.test:
        pendingCount = int(subprocess.check_output('bjobs -p 2> /dev/null | wc -l', shell=True))
        while pendingCount > 10 : 
            sys.stdout.write( 'Total jobs pending: %s\r' % pendingCount )
            sys.stdout.flush()
            time.sleep(1)
            pendingCount = int(subprocess.check_output('bjobs -p 2> /dev/null | wc -l',shell=True))

        if pendingCount > 0 :
            time.sleep(10)
    #end if not test

    config_args = args.config_args+' --run_number %d'%job

    specific_command = command + " \"%s\""%(config_args)
    
    if args.input_dir is not None :
        specific_command += " %s"%os.path.join(full_input_dir,inputFileList[job-args.start_job])
    #end attachment of input file

    full_cmd=args.batch_cmd+' '+specific_command
    if args.test: 
        print(full_cmd)
    else:
        subprocess.Popen(full_cmd,shell=True,encoding='utf8').wait()
        time.sleep(1)
    #end whether or not is a test
#end loop through jobs
