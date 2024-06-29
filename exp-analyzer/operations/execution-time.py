import pstats
from pstats import Stats
import glob

def compute_function_times_per_file(files, function_name):
    function_times = {}
    
    for file in files:
        p = pstats.Stats(file)
        p.strip_dirs().sort_stats('cumulative')
        for func, stat in p.stats.items():
            if function_name in pstats.func_std_string(func):
                total_time = stat[3]  # Cumulative time spent in the given function
                call_count = stat[0]  # Number of calls to the function
                time_per_call = total_time / call_count if call_count != 0 else 0
                function_times[file] = (total_time, time_per_call)
    
    return function_times

def print_function_times(function_times):
    sorted_files = sorted(function_times.items(), key=lambda x: x[1][0], reverse=True)
    
    for file, (cum_time, time_per_call) in sorted_files:
        print(f"{file}: {cum_time:.6f} seconds, {time_per_call:.6f} seconds per call")

def main():
    # Adjust the path to match where your .pstats files are located
    filesdir = '/Users/mustafafaisal/Desktop/cpy-runtime/*.prof'
    files = glob.glob(filesdir)

    if not files:
        print("No pstats files found.")
        return

    # Get the function name from the user
    function_name = 'evaluate' #input("Enter the function name: ")

    function_times = compute_function_times_per_file(files, function_name)
    if not function_times:
        print(f"No data found for function: {function_name}")
    else:
        print(f"Cumulative times for function '{function_name}':")
        print_function_times(function_times)

if __name__ == "__main__":
    main()