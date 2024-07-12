import pstats
from pstats import Stats
import glob

def compute_function_times_per_file(files, function_name):
    function_times = {}
    
    for file in files:
        p = pstats.Stats(file)
        p.strip_dirs().sort_stats('cumulative')
        history_calls = []
        for func, stat in p.stats.items():
            if function_name in pstats.func_std_string(func):
                total_time = stat[3]  # Cumulative time spent in the given function
                call_count = stat[0]  # Number of calls to the function
                time_per_call = total_time / call_count if call_count != 0 else 0
                function_times[file] = (total_time, time_per_call)
    
    return function_times

def save_function_times(function_name, function_times):
    sorted_files = sorted(function_times.items(), key=lambda x: x[1][1], reverse=True)
    
    with open(f"{function_name}.log", "w") as f:
        for file, (cum_time, time_per_call) in sorted_files:
            f.write(f"{file}: {cum_time:.6f} seconds, {time_per_call:.6f} seconds per call\n")

def sort_files_by_cumulative_time(files):
    cumulative_times = {}

    for file in files:
        p = pstats.Stats(file)
        p.strip_dirs().sort_stats('cumulative')
        total_cumulative_time = sum(stat[3] for func, stat in p.stats.items())
        cumulative_times[file] = total_cumulative_time

    sorted_files = sorted(cumulative_times.keys(), key=lambda x: cumulative_times[x], reverse=True)
    with open("sorted_files_by_cumulative_time.log", "w") as f:
        for file in sorted_files:
            f.write(f"{file}: {cumulative_times[file]:.6f} seconds\n")



def main():
    # Adjust the path to match where your .pstats files are located
    filesdir = '/home/ma342/developer/dev-pybehaviour-planning-eval/sandbox-runtime-profiling-solve/*.prof'
    files = glob.glob(filesdir)

    if not files:
        print("No pstats files found.")
        return

    # Get the list of function names from the user
    function_names = [
        # 'cost_bound_makespan_optimal.py:10(__init__)',
        # 'cost_bound_makespan_optimal.py:13(__encode__)',
        # 'smt_sequential_plan.py:49(cost)',
        # 'seq_encoder.py:110(extract_plan)',
        # 'basic.py:85(extract_plan)',
        # 'str',
        # 'plan_behaviour', 
        # 'check', 
        # 'extract_plan', 
        # 'infer_behaviour',
        'generate_summary_file'
    ]

    for function_name in function_names:
        function_name = function_name.strip()
        function_times = compute_function_times_per_file(files, function_name)
        if not function_times:
            print(f"No data found for function: {function_name}")
        else:
            save_function_times(function_name, function_times)
            print(f"Results for function '{function_name}' have been saved to '{function_name}.log'")

    sort_files_by_cumulative_time(files)

if __name__ == "__main__":
    main()
