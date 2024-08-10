import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import deque, defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
from copy import deepcopy
from scipy.interpolate import interp1d


class Activity:
    def __init__(self, name, optimistic, most_likely, pessimistic, duration, activity_name):
        self.name = name
        self.optimistic = optimistic
        self.most_likely = most_likely
        self.pessimistic = pessimistic
        self.duration = duration
        self.predecessors = []
        self.successors = []
        self.early_start = 0
        self.early_finish = 0
        self.late_start = 0
        self.late_finish = 0
        self.total_float = 0
        self.free_float = 0
        self.critical_count = 0
        self.activity_name = activity_name


def add_activity(activities, name, optimistic, most_likely, pessimistic, duration, activity_name):
    activities[name] = Activity(
        name, optimistic, most_likely, pessimistic, duration, activity_name)


def add_predecessor(activities, activity_name, predecessor_name):
    activities[activity_name].predecessors.append(predecessor_name)
    activities[predecessor_name].successors.append(activity_name)


def process_wbs(wbs_element, activities):
    try:
        if wbs_element['Type'] == 'Activity':
            add_activity(
                activities,
                wbs_element['PMINumber'],
                wbs_element['ThreePointEstimate']['Optimistic'],
                wbs_element['ThreePointEstimate']['MostLikely'],
                wbs_element['ThreePointEstimate']['Pessimistic'],
                wbs_element['Duration'],
                wbs_element['Name']
            )
            if 'Predecessors' in wbs_element:
                for predecessor in wbs_element['Predecessors']:
                    add_predecessor(
                        activities, wbs_element['PMINumber'], predecessor)
        elif 'Children' in wbs_element:
            for child in wbs_element['Children']:
                process_wbs(child, activities)
    except KeyError as e:
        raise ValueError(f"Missing key in WBS element: {str(e)}")


def topological_sort(activities):
    in_degree = {name: 0 for name in activities}
    for activity in activities.values():
        for successor in activity.successors:
            in_degree[successor] += 1

    queue = deque([name for name in activities if in_degree[name] == 0])
    topo_order = []

    while queue:
        current = queue.popleft()
        topo_order.append(current)
        for successor in activities[current].successors:
            in_degree[successor] -= 1
            if in_degree[successor] == 0:
                queue.append(successor)

    # Detect cycle
    if len(topo_order) != len(activities):
        raise Exception("Cyclic dependencied in project!")

    return topo_order


def simulate_project(activities, topo_order):

    for activity in activities.values():
        activity.early_start = 0
        activity.late_start = 0
        activity.late_finish = 0

    simulated_durations = {}
    # calculate early times

    for name in topo_order:
        activity = activities[name]
        duration = np.random.triangular(
            activity.optimistic, activity.most_likely, activity.pessimistic)
        activity.duration = duration
        activity.early_finish = activity.early_start + activity.duration
        simulated_durations[name] = duration
        for successor in activity.successors:
            successor_activity = activities[successor]
            successor_activity.early_start = max(
                successor_activity.early_start, activity.early_finish)

    end_time = max(activity.early_finish for activity in activities.values())

    for name in reversed(topo_order):
        activity = activities[name]
        activity.late_finish = activity.late_finish or end_time
        activity.late_start = activity.late_finish - activity.duration
        for predecessor in activity.predecessors:
            predecessor_activity = activities[predecessor]
            predecessor_activity.late_finish = min(
                predecessor_activity.late_finish, activity.late_start) if predecessor_activity.late_finish else activity.late_start

        # Calculate float and identify critical path
    critical_path = []
    for name, activity in activities.items():
        activity.total_float = activity.late_start - activity.early_start
        if activity.total_float == 0:
            critical_path.append(name)

    project_duration = max(
        activity.early_finish for activity in activities.values())

    return project_duration, simulated_durations, critical_path


def monte_carlo_simulation(activities, topo_order, num_simulations=10000):

    if num_simulations <= 0:
        raise Exception("invalid number of simulations")

    project_durations = []
    duration_records = defaultdict(list)

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(simulate_project, deepcopy(
            activities), topo_order) for _ in range(num_simulations)]
        for future in as_completed(futures):
            project_duration, simulated_durations, critical_path = future.result()
            project_durations.append(project_duration)

            # add the simulated duration record of each activity for each simulation
            for name, duration in simulated_durations.items():
                duration_records[name].append(duration)

        # Accumulate critical counts
            for name in critical_path:
                # Increment critical count for critical activities
                activities[name].critical_count += 1

    return project_durations, duration_records

# Determine the actual project duration based on the baseline critical path


def calculate_baseline_duration(activities, topo_order):
    for activity in activities.values():
        activity.early_start = 0
        activity.late_start = 0
        activity.late_finish = 0

    simulated_durations = {}
    # calculate early times

    for name in topo_order:
        activity = activities[name]
        duration = activity.most_likely
        activity.duration = duration
        activity.early_finish = activity.early_start + activity.duration
        simulated_durations[name] = duration
        for successor in activity.successors:
            successor_activity = activities[successor]
            successor_activity.early_start = max(
                successor_activity.early_start, activity.early_finish)

    end_time = max(activity.early_finish for activity in activities.values())

    for name in reversed(topo_order):
        activity = activities[name]
        activity.late_finish = activity.late_finish or end_time
        activity.late_start = activity.late_finish - activity.duration
        for predecessor in activity.predecessors:
            predecessor_activity = activities[predecessor]
            predecessor_activity.late_finish = min(
                predecessor_activity.late_finish, activity.late_start) if predecessor_activity.late_finish else activity.late_start

    project_duration = max(
        activity.early_finish for activity in activities.values())

    return project_duration


def summarize_results(durations):
    mean_duration = np.mean(durations)
    p50 = np.percentile(durations, 50)
    p80 = np.percentile(durations, 80)
    p90 = np.percentile(durations, 90)

    return {
        'Mean Duration': mean_duration,
        'P50': p50,
        'P80': p80,
        'P90': p90
    }


def sensitivity_analysis(project_durations, duration_records, activities):
    sensitivity_results = {}

    for name, durations in duration_records.items():
        if len(durations) != len(project_durations):
            raise ValueError(
                f"Mismatch in number of simulations for activity {name}")
        correlation = np.corrcoef(durations, project_durations)[0, 1]
        
        sensitivity_results[name] = {"name": activities[name].activity_name, "value": correlation}

    return sensitivity_results


def calculate_criticality_index(activities, num_simulations):
    return {name: {"name": activity.activity_name, "value": activity.critical_count / num_simulations} for name, activity in activities.items()}


def calculate_significance_index(duration_records, project_durations, activities):
    significance_results = {}

    mean_project_duration = np.mean(project_durations)

    for name, durations in duration_records.items():
        significance_results[name] =  {"name": activities[name].activity_name, "value": np.mean(durations) / mean_project_duration} 

    return significance_results


def validate_schedule_input(schedule):
    """Validates the structure and content of the schedule input."""
    if 'WBS' not in schedule:
        raise ValueError("Schedule is missing the 'WBS' element.")

    if not isinstance(schedule['WBS'], list):
        raise ValueError("'WBS' element must be a list.")

    for element in schedule['WBS']:
        validate_wbs_element(element)


def validate_wbs_element(element):
    """Validates an individual WBS element."""
    if element['Type'] == 'Activity':
        required_fields = ['PMINumber',
                           'ThreePointEstimate', 'Predecessors', 'Duration']
        for field in required_fields:
            if field not in element:
                raise ValueError(f"Activity is missing the '{field}' field.")

        # Additional validation for ThreePointEstimate (ensure it's a dict with correct keys)
        if not isinstance(element['ThreePointEstimate'], dict) or \
           not all(key in element['ThreePointEstimate'] for key in ['Optimistic', 'MostLikely', 'Pessimistic']):
            raise ValueError(
                "Activity has invalid 'ThreePointEstimate' format.")

    elif 'Children' in element:
        for child in element['Children']:
            validate_wbs_element(child)


def generate_hist_cdf(durations):

    counts, bin_edges = np.histogram(durations, bins=50)

    # Step 2: Calculate cumulative distribution
    cumulative_counts = np.cumsum(counts)
    cumulative_probabilities = cumulative_counts / \
        cumulative_counts[-1]  # Normalize to get probabilities

    bin_edges_cdf = bin_edges[:-1]

    # Interpolate to create a smooth curve
    interpolation_function = interp1d(
        bin_edges_cdf, cumulative_probabilities, kind='cubic')

    # Generate more points for a smooth line
    x_new = np.linspace(bin_edges_cdf.min(), bin_edges_cdf.max(), 500)
    y_smooth = interpolation_function(x_new)

    return {"hist": {
        "counts": counts.tolist(),
        "bin_edges": bin_edges.tolist()
    },
        "cdf": {
        "project_duration": x_new.tolist(),
        "cumulative_probability": y_smooth.tolist()
    }}


def perform_sra(schedule, num_simulations=3000):

    validate_schedule_input(schedule)

    # make activities
    activities = {}

    # Process the WBS from the JSON
    for element in schedule['WBS']:
        process_wbs(element, activities)

       # Topological sort with cycle detection
    try:
        topo_order = topological_sort(activities)
    except ValueError as e:
        return {"error": str(e)}

    # monte carlo simulations

    project_durations, duration_records = monte_carlo_simulation(
        activities, topo_order, num_simulations)
    results = summarize_results(project_durations)
    baseline_duration = calculate_baseline_duration(activities, topo_order)
    criticality_index = calculate_criticality_index(
        activities, num_simulations)
    sensitivity_results = sensitivity_analysis(
        project_durations, duration_records, activities)
    significance_index = calculate_significance_index(
        duration_records, project_durations, activities)

    project_hist_cdf = generate_hist_cdf(project_durations)

    return {"project_hist_cdf": project_hist_cdf, "results": results, "baseline_duration": baseline_duration,
            "criticality_index": criticality_index,  "sensitivity_results": sensitivity_results, "significance_index": significance_index}
