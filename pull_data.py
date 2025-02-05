import itertools
import subprocess
import sys
import apply_templates


class BuildConfig:

    work_group_size: str
    selected_kernel: str
    cl_compiler_options: str

    def __init__(
        self,
        work_group_size="32",
        selected_kernel="9",
        cl_compiler_options=""
    ):
        self.work_group_size = work_group_size
        self.selected_kernel = selected_kernel
        self.cl_compiler_options = cl_compiler_options

    def apply_template(self):
        templates = [
            apply_templates.FileTemplate("templates/settings.h", "src/settings.h", {
                "SELECTED_KERNEL": self.selected_kernel,
                "WORK_GROUP_SIZE": self.work_group_size,
                "CL_COMPILER_OPTIONS": self.cl_compiler_options,
            })
        ]

        for t in templates:
            t.replace()


def run_make():
    subprocess.run(['make', 'build', *sys.argv[1:]], check=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)


def collect_data_for_config():
    output = subprocess.run(['./bin/myGEMM'], check=True, capture_output=True)
    data = output.stdout.decode().split('##')[1].strip().split('\n')
    header = data[1]
    bench_data = data[2:]
    print('\n'.join(bench_data))


def benchmark_with(config: BuildConfig):
    config.apply_template()
    run_make()
    return collect_data_for_config()


if __name__ == '__main__':
    WORK_GROUP_SIZES = [
        8, 16, 32
        #32, 16
    ]

    SELECTED_KERNELS = [
        #1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11
        3, 4, 5, 6, 7
        #1, 2
    ]

    ALL_CL_COMPILER_OPTIONS = [
        "-cl-std=CL2.0",
        "-cl-std=CL1.2"
    ]

    variables = [ALL_CL_COMPILER_OPTIONS, SELECTED_KERNELS, WORK_GROUP_SIZES]

    for combination in itertools.product(*variables):
        compiler_options, kernel, wgs = combination

        config = BuildConfig(
            work_group_size=wgs,
            selected_kernel=kernel,
            cl_compiler_options=compiler_options
        )

        benchmark_with(config)