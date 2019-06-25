import os
import shutil
import git
import copy
import sys
import subprocess
import glob
import ismo.submit


def all_successfully_completed():
    lsf_files = glob.glob('lsf.o*')

    for lsf_filename in lsf_files:
        with open(lsf_filename) as f:
            content = f.read()


            if 'Successfully completed' not in content:
                return False

    return True


def get_configuration_name(basename, iteration_sizes):
    return f'{basename}_iterations_{"_".join(map(str, iteration_sizes))}'



def run_configuration(*, basename, 
                      reruns,  
                      iteration_sizes, 
                      repository_path,
                      dry_run, 
                      experiment,
                      memory,
                      submitter,
                      generator):
    iteration_sizes_as_str = [str(x) for x in iteration_sizes]
    working_dir = os.path.dirname(experiment)
    experiment_base = os.path.basename(experiment)
    command_to_submit_list = [
        sys.executable,
        experiment_base,
        '--number_of_samples_per_iteration',
        *iteration_sizes_as_str,
        '--retries',
        str(reruns),
        '--generator',
        generator
    ]

    command = ismo.submit.Command(command_to_submit_list)
    old_dir = os.getcwd()
    os.chdir(working_dir)
    submitter(command,
              number_of_processes=1,
              wait_time_in_hours=120,
              memory_limit_in_mb=memory)

    os.chdir(old_dir)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="""
Runs the ensemble for M different runs (to get some statistics)./

""")

    parser.add_argument('--number_of_reruns', type=int, default=10,
                        help='Total number of reruns to get the ensemble')


    parser.add_argument('--basename', type=str, default='ensemble_run',
                        help='Basename for the ensemble')

    parser.add_argument('--compute_budget', type=int, default=512,
                        help='Maximum compute budget (in terms of number of samples that can be computed from simulator)')

    parser.add_argument('--starting_sizes', type=int, nargs='+', default=[16, 32, 64],
                        help='Starting sizes to use')

    parser.add_argument('--batch_size_factors', type=float, nargs='+', default=[0.5, 1],
                        help='Batch sizes to use as a ratio of starting_size')


    repo = git.Repo(search_parent_directories=True)

    parser.add_argument('--repository_path', type=str, default=repo.working_dir,
                        help='Absolute path of the repository')

    parser.add_argument('--dry_run', action='store_true',
                        help='Only do a dry run, no jobs are submitted or run')

    parser.add_argument('--only_missing', action='store_true',
                        help='Only run missing configurations')


    parser.add_argument('--experiment', type=str,
                        help='Path to python experiment file')
    
    parser.add_argument('--memory', type=int, default=4000,
                        help="Memory per process (in MB)")

    parser.add_argument('--submitter', type=str, default='bash',
                        help="Submitter (either bash or lsf)")

    parser.add_argument('--generator', type=str, default='monte-carlo',
                        help="Generator (either 'monte-carlo' or 'sobol')")
    
    


    args = parser.parse_args()

    submitter = ismo.submit.create_submitter(args.submitter, None, dry_run=args.dry_run)


    for starting_size in args.starting_sizes:
        for batch_size_factor in args.batch_size_factors:
            iteration_sizes = [starting_size]

            while sum(iteration_sizes) < args.compute_budget:
                iteration_sizes.append(int(batch_size_factor*starting_size))

            run_configuration(basename=args.basename,
                              reruns=args.number_of_reruns,
                              iteration_sizes=iteration_sizes,
                              repository_path=args.repository_path,
                              dry_run=args.dry_run,
                              experiment=args.experiment,
                              memory=args.memory,
                              submitter=submitter,
                              generator=args.generator)




