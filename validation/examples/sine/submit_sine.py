import ismo.submit
import ismo.submit.defaults
import sys

class SineCommands(ismo.submit.defaults.Commands):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def do_evolve(self, submitter,
                  *,
                  iteration_number: int,
                  input_parameters_file: str,
                  output_value_files: list):
        command = ismo.submit.Command([self.python_command, 'evolve_sine.py'])

        command = command.with_long_arguments(input_parameters_file=input_parameters_file,
                                              output_values_file=output_value_files)

        submitter(command, wait_time_in_hours=24)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="""
Submits all the jobs for the sine experiments
        """)

    parser.add_argument('--number_of_samples_per_iteration', type=int, nargs='+',
                        help='Number of samples per iteration')

    parser.add_argument('--chain_name', type=str, default="sine",
                        help="Name of the chain to run")

    parser.add_argument('--prefix', type=str, default="",
                        help="Prefix of files")

    parser.add_argument('--submitter', type=str, required=True,
                        help='Submitter to be used. Either "bash" (runs without waiting) or "lsf"')

    parser.add_argument('--dry_run', action='store_true',
                        help="Don't actually run the command, only print the commands that are to be executed")

    parser.add_argument('--starting_sample', type=int, default=0,
                        help='Starting sample')

    parser.add_argument('--generator', type=str, default='monte-carlo',
                        help='Generator name')

    args = parser.parse_args()

    submitter = ismo.submit.create_submitter(args.submitter, args.chain_name, dry_run=args.dry_run)

    commands = SineCommands(dimension=1,
                            training_parameter_config_file='training_parameters.json',
                            optimize_target_file='objective.py',
                            optimize_target_class='Objective',
                            python_command=sys.executable,
                            starting_sample=args.starting_sample,
                            prefix=args.prefix,
                            sample_generator_name=args.generator
                            )

    chain = ismo.submit.Chain(args.number_of_samples_per_iteration, submitter,
                              commands=commands)

    chain.run()
