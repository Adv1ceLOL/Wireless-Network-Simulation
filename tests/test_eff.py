
import csv
import os
import subprocess
import re

probs = [x / 100.0 for x in range(10, 30, 10)]

def gen_csv():
    """Generate CSV with parameter combinations"""
    file = open("file.csv", 'w')
    for nodes in range(10, 50, 20):
        for time_steps in [30, 60, 100, 1000]:
            for pfail in probs:
                for pnew in probs:
                    for req in [15, 35, 65, 85, 100]:
                        preq = req/100
                        line = f"{nodes},{time_steps},{pfail},{pnew},{preq}\n"
                        file.write(line)
    file.close()
    print(f"Generated reduced parameter combinations: 3*3*3*3*3 = 243 total tests")

def load_csv(filename="file.csv"):
    """Load parameter combinations from CSV"""
    params = []
    with open(filename, "r") as file:
        reader = csv.reader(file)
        for row in reader:
            # row is a list of strings, convert to numbers as needed
            nodes = int(row[0])
            time_steps = int(row[1])
            pfail = float(row[2])
            pnew = float(row[3])
            preq = float(row[4])
            
            # store in a tuple (or list if you prefer)
            params.append((nodes, time_steps, pfail, pnew, preq))
    return params

def extract_efficiency_from_output(output):
    """Extract efficiency and message percentages from simulation output."""
    try:
        # Extract efficiency
        efficiency_match = re.search(r'Protocol Efficiency: ([\d.]+) \(([\d.]+)%\)', output)
        if not efficiency_match:
            return None
            
        efficiency_pct = float(efficiency_match.group(2))
        
        # Extract message percentages
        hello_match = re.search(r'Hello Messages\s+\|\s+(\d+)\s+\|\s+([\d.]+)%', output)
        topology_match = re.search(r'Topology Messages\s+\|\s+(\d+)\s+\|\s+([\d.]+)%', output)
        route_match = re.search(r'Route Discovery\s+\|\s+(\d+)\s+\|\s+([\d.]+)%', output)
        data_match = re.search(r'Data Packets\s+\|\s+(\d+)\s+\|\s+([\d.]+)%', output)
        
        if not all([hello_match, topology_match, route_match, data_match]):
            return None
            
        return {
            'efficiency_pct': efficiency_pct,
            'hello_pct': float(hello_match.group(2)),
            'topology_pct': float(topology_match.group(2)),
            'route_pct': float(route_match.group(2)),
            'data_pct': float(data_match.group(2))
        }
    except:
        return None

def run_simulation_and_save_results():
    """Run all simulations and save results to prove.txt"""
    
    # Generate parameter combinations
    gen_csv()
    all_params = load_csv()
    
    # Open results file
    with open("efficiency_results.txt", "w") as results_file:
        results_file.write("# COMPREHENSIVE EFFICIENCY RESULTS\n")
        results_file.write("# nodes|steps|p_fail|p_new|p_request|efficiency%|hello%|topology%|route%|data%\n")
        results_file.write("#" + "="*80 + "\n")
        
        total_runs = len(all_params)
        completed = 0
        
        for line in all_params:
            nodes, time_steps, pfail, pnew, preq = line
            
            cmd = [
                "python", "simulation.py",
                "--nodes", str(nodes),
                "--time-steps", str(time_steps),
                "--seed", "1",
                "--p-fail", str(pfail),
                "--p-new", str(pnew),
                "--p-request", str(preq),
                "--no-interactive"
            ]
            
            completed += 1
            print(f"Progress: {completed}/{total_runs} ({completed/total_runs*100:.1f}%) - Running: nodes={nodes}, steps={time_steps}, p_fail={pfail}, p_new={pnew}, p_request={preq}")
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                
                # Try to extract efficiency data even if return code is non-zero
                # The Unicode error occurs AFTER efficiency calculation
                efficiency_data = extract_efficiency_from_output(result.stdout)
                
                if efficiency_data:
                    # Write result to file
                    line_result = f"{nodes:2d}|{time_steps:3d}|{pfail:4.2f}|{pnew:4.2f}|{preq:4.2f}|{efficiency_data['efficiency_pct']:6.2f}|{efficiency_data['hello_pct']:5.1f}|{efficiency_data['topology_pct']:5.1f}|{efficiency_data['route_pct']:5.1f}|{efficiency_data['data_pct']:5.1f}\n"
                    results_file.write(line_result)
                    results_file.flush()  # Ensure data is written immediately
                    print(f"  SUCCESS: Efficiency = {efficiency_data['efficiency_pct']:.2f}%")
                else:
                    print(f"  WARNING: Could not extract efficiency data")
                    if result.returncode != 0:
                        print(f"  ERROR: Simulation failed with return code {result.returncode}")
                        if result.stderr:
                            print(f"  STDERR: {result.stderr[:200]}...")
                    
            except subprocess.TimeoutExpired:
                print(f"  TIMEOUT: Simulation took too long")
            except Exception as e:
                print(f"  EXCEPTION: {e}")

if __name__ == "__main__":
    # Run the comprehensive test
    print("Starting comprehensive efficiency testing...")
    print("This will take a while - generating thousands of parameter combinations...")
    run_simulation_and_save_results()
    print("Results saved to efficiency_results.txt")
