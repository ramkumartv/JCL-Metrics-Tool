import glob
import re
import os
from pathlib import Path
from datetime import *
from configuration import *

input_jcl_path = f"{input_job_path}*.*"
list_of_files = glob.glob(input_jcl_path)

def jcl_expansion(list_of_files):
    for job_names in list_of_files:
        job_name = open(job_names, 'r')
        job_line = job_name.readlines()

        f1 = open(os.path.join(expanded_jcl_path,
                               os.path.basename(job_names)), 'w')

        for line in job_line:
            execstr = [" EXEC "]
            pgmstr = ["PGM="]
            f1.writelines(line)
            if execstr[0] in line:
                if pgmstr[0] not in line:
                    line = re.split('[,| |\n]+', line)
                    proc_name = line[2]
                    proc_name.strip()
                    procname = proc_name + '.txt'
                    filepath = os.path.join(input_proc_path, procname)
                    try:
                        f1 = open(filepath, 'r')

                        lst1 = []

                        for line1 in f1:
                            line1.strip()
                            lst1.append(line1)

                        f1 = open(os.path.join(expanded_jcl_path,
                                           os.path.basename(job_names)), 'a')

                        for line1 in lst1:
                            if not line1.isspace():
                                f1.write(line1)
                        f1.write("\n")
                    except:
                        current_date = date.today()
                        current_time = datetime.now().strftime("%H-%M-%S")
                        errfilename = "Error_file_" + str(current_date) + "_" + str(current_time)
                        jobname = (os.path.basename(job_names))
                        error_text = f"{procname} PROC not found in job {jobname}"
                        error_file = errfilename + ".txt"
                        error_dir_path = Path(errorfile_path)
                        if error_dir_path.is_dir():
                            with open(error_dir_path.joinpath(error_file), 'a') as f2:
                                f2.write(error_text + "\n")
                        else:
                            print("Error file directory doesn't exist")

jcl_expansion(list_of_files)
print("JCL expanded with PROC ")

def jcl_metrics():
    input_path = f"{expanded_jcl_path}*.*"
    list_of_files = glob.glob(input_path)
    sno = 0

    for f in os.listdir(output_stats_path):
        os.remove(os.path.join(output_stats_path, f))

    header = f"S.No , Job name , Lines of Code , Commented Lines , Step Count ," \
             f" DD statement Count, Program count, Db2 Program Count, JCL Utilities"
    out_file = 'JCL_Metrics.csv'
    dir_path = Path(output_stats_path)

    if dir_path.is_dir():
        with open(dir_path.joinpath(out_file), 'a') as f:
                f.write(header + "\n")
    else:
        print("Directory doesn't exist")

    for job_names in list_of_files:
        job_name = open(job_names, 'r')
        job_line = job_name.readlines()
        linecount = 0
        commentcount, stepcount, ddcount , db2count, utilcount , pgmcount = 0 , 0 , 0 , 0 , 0 , 0
        execstr = " EXEC "
        pgmstr = "PGM="
        comstr = "//*"
        ddstr  = " DD "
        utilstr = [""]
        db2prog = ["IKJEFT01","IKJEFT1A","IKJEFT1B"]
        jclutil = ["IEBCOPY","IEBGENER","IEHLIST","IEHMOVE","IEBCOMPR","IEBEDIT",
                   "IEHPROGM","DFSORT","SYNCSORT","ICETOOL","IDCAMS","IEFBR14"]
        file_name = os.path.basename(job_names).split('.')[0]
        sno += 1

        for line in job_line:
            linecount += 1

            if str(line[0:3]) == comstr:
                commentcount += 1
            if execstr in line and pgmstr in line and str(line[0:3]) != comstr:
                stepcount += 1
            if ddstr in line and str(line[0:3]) != comstr:
                ddcount += 1
            for db2emt in db2prog:
                if db2emt in line and pgmstr in line and str(line[0:3]) != comstr:
                    db2count += 1
            for jclemt in jclutil:
                if jclemt in line and pgmstr in line and str(line[0:3]) != comstr:
                    utilcount += 1

        pgmcount = stepcount - db2count - utilcount
        line1 = f"{sno} , {file_name} , {linecount} , {commentcount} ,  {stepcount} ,  {ddcount} ," \
                f" {pgmcount} , {db2count} , {utilcount} "
        out_file = 'JCL_Metrics.csv'
        dir_path = Path(output_stats_path)
        if dir_path.is_dir():
            with open(dir_path.joinpath(out_file), 'a') as f:
                f.write(line1 + "\n")
        else:
            print("Directory doesn't exist")

jcl_metrics()
print("JCL Statistics written to output metrics file")