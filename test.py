import subprocess

# Define the command to execute
value = "dir"

def execute_dir_command(command):
    # Execute the command
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    # Print the command output directly
    print("Command Output:\n")
    print(result.stdout)  # Print the standard output of the command
    print("Error Output:\n")
    print(result.stderr)   # Print the error output if any

# Example usage
execute_dir_command(value)