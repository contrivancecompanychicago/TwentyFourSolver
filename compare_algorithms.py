"""
This script runs a multitude of tests on both algorithms to compare their performance.
"""

import sys
import subprocess
from itertools import combinations_with_replacement
from itertools import izip

MAX_NUM_TESTS = -1
INCLUDE_NO_SOLUTION_CARDS = True
MAX_CARD_NUMBER = 14
REPORT_EVERY_N_TESTS = 50
REPORT_EVERY_N_RESULTS = 2000
NUM_LINES_PER_RESULT = 2
REPORT_EVERY_N_LINES = NUM_LINES_PER_RESULT * REPORT_EVERY_N_RESULTS
SOLUTION_INDICATOR_STR = "Solution:"
NO_SOLUTION_INDICATOR_STR = "No solution found."
ATTEMPTS_INDICATOR_STR = "Number of attempts:"

class TestResult(object):
    """
    Represents the solution to a card and the number of attempts it took to reach it
    """
    def __init__(self, solution, attempts):
        self.solution = solution
        self.attempts = attempts

def extract_data_from_output(file):
    """
    Extracts useful data about the performance of an algorithm
    :param file: The output file holding the output of all the tests for an algorithm
    :return: A list of TestResult instances
    """
    data = []
    num_lines_read = 0

    line = file.readline()
    while line != "":
        num_lines_read += 1

        # Print a progress update if necessary
        if num_lines_read % REPORT_EVERY_N_LINES == 0:
            num_results_processed = num_lines_read / NUM_LINES_PER_RESULT
            print "%s Results processed" % num_results_processed

        # See if this line begins the output for a test case
        if SOLUTION_INDICATOR_STR in line or  NO_SOLUTION_INDICATOR_STR in line:
            # If so, extract the solution and the number of attempts
            index = line.find(SOLUTION_INDICATOR_STR)
            solution = ""
            if index >= 0:
                end_index = index + len(SOLUTION_INDICATOR_STR)
                solution = line[end_index:]
            else:
                solution = "No solution"
            # print solution

            # Extract the number of attempts from the next line
            num_lines_read += 1
            line = file.readline()
            if ATTEMPTS_INDICATOR_STR in line:
                # If so, extract the number of solutions
                index = line.find(ATTEMPTS_INDICATOR_STR)
                end_index = index + len(ATTEMPTS_INDICATOR_STR)
                num_attempts = int(line[end_index:])
                data.append(TestResult(solution, num_attempts))
                # print num_attempts

        line = file.readline()

    return data

def average_num_attempts(data):
    """
    Finds the average number of attempts for an algorithm given its data
    :param data: The dictionary returned from the extract_data_from_output() method
    :return: The average number of attempts
    """
    total = 0
    for test_result in data:
        if INCLUDE_NO_SOLUTION_CARDS or test_result.solution != "No solution":
            attempts = test_result.attempts
            total += attempts
    return total / len(data)


# Callable command line statements
execute_brute_force_algorithm = ['python', 'brute_force_algorithm.py']
execute_my_algorithm = ['python', 'my_algorithm.py']

# Two lists of strings to keep track of the algorithms' output
brute_force_output = []
my_output = []

# Keep track of how many cards we're testing
total_to_test = MAX_NUM_TESTS if MAX_NUM_TESTS != -1 \
    else len(list(combinations_with_replacement(range(1, MAX_CARD_NUMBER), 4)))
current_test = 0
print "Total cards to test: %s" % total_to_test

# Test all possible 24 Cards (unless MAX_NUM_TESTS is specified)
for card in combinations_with_replacement(range(1, MAX_CARD_NUMBER), 4):
    current_test += 1
    if current_test % REPORT_EVERY_N_TESTS == 0:
        print "%s Cards tested" % current_test

    # print card

    # Convert card to an array of strings
    card_as_str = []
    for num in card:
        card_as_str.append(str(num))

    # Solve the card with both algorithms and append the output to the proper lists
    brute_force_command = execute_brute_force_algorithm + card_as_str
    my_command = execute_my_algorithm + card_as_str

    brute_force_output.append(subprocess.check_output(brute_force_command))
    my_output.append(subprocess.check_output(my_command))

    # Stop if MAX_NUM_TESTS is specified
    if MAX_NUM_TESTS != -1 and current_test > MAX_NUM_TESTS:
        break

print "All tests completed."

print "Writing output files..."

# Write the big huge output strings to two files
brute_force_output_file = open('brute_force_output.txt', 'w')
my_output_file = open('my_output.txt', 'w')

join_str = ""
brute_force_output_file.write(join_str.join(brute_force_output))
my_output_file.write(join_str.join(my_output))

# Clear the big huge strings to free memory
brute_force_output = []
my_output = []

# Close the files
brute_force_output_file.close()
my_output_file.close()

print "Done."
print
print "Processing results..."

# Reopen the files as read-only
brute_force_output_file = open('brute_force_output.txt', 'r')
my_output_file = open('my_output.txt', 'r')

# Extract the data from the files
brute_force_data = extract_data_from_output(brute_force_output_file)
my_data = extract_data_from_output(my_output_file)

# Close the files
brute_force_output_file.close()
my_output_file.close()


# Interpret the data we collected

# First, we can find the average number of attempts for each algorithm
brute_force_average = average_num_attempts(brute_force_data)
my_average = average_num_attempts(my_data)

# Second, we can also see how many times each algorithm won
# And we can detect discrepancies between their solutions

brute_force_victories = 0
my_victories = 0
num_discrepancies = 0

if len(brute_force_data) != len(my_data):
    print "Unexpected: Number of test results for each algorithm are not the same."
    print "Number of results for brute-force algorithm: %s" % len(brute_force_data)
    print "Number of results for my algorithm: %s" % len(my_data)
    sys.exit(1)

for brute_force_test_result, my_test_result in izip(brute_force_data, my_data):
    # See who won (if not INCLUDE_NO_SOLUTION, check that there was a solution for both)
    is_brute_force_solution = brute_force_test_result.solution != "No solution"
    is_my_solution = my_test_result.solution != "No solution"
    if INCLUDE_NO_SOLUTION_CARDS or (is_brute_force_solution and is_my_solution):
        brute_force_attempts = brute_force_test_result.attempts
        my_attempts = my_test_result.attempts
        if my_attempts < brute_force_attempts:
            my_victories += 1
        else:
            brute_force_victories += 1

    # Check if they arrived at the same solution
    brute_force_solution = brute_force_test_result.solution
    my_solution = my_test_result.solution
    if brute_force_solution != my_solution:
        num_discrepancies += 1

# More calculations
my_winning_percentage = float(my_victories) / (my_victories + brute_force_victories) * 100
my_algorithm_times_faster = float(brute_force_average) / my_average

print "All results processed."
print
print "Findings:"

no_solution_str = "when cards with no solution are included" if INCLUDE_NO_SOLUTION_CARDS \
    else "not including cards with no solution"

# Print out the findings
print "Average number of attempts for brute-force: %s" % brute_force_average
print "Average number of attempts for my algorithm: %s" % my_average
print "Brute-force victories: %s" % brute_force_victories
print "My algorithm victories: %s" % my_victories
print "Number of cards where different solutions were reached: %s" % num_discrepancies
print
print "THE VERDICT:"
print "My algorithm outperforms the brute-force algorithm %.2f%% of the time (%s)" \
      % (my_winning_percentage, no_solution_str)
print "On average, my algorithm is %.1f times faster than the brute-force algorithm (%s)" \
      % (my_algorithm_times_faster, no_solution_str)
