from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Store the latest command output to display
command_output = {"stdout": "", "stderr": ""}

@app.route('/')
def index():
    return render_template('index.html', command_output=command_output)

@app.route('/receive_output', methods=['POST'])
def receive_output():
    global command_output

    # Get the JSON data from the request
    output = request.get_json()

    if output:
        # Update the command output
        command_output['stdout'] = output.get('stdout', '')
        command_output['stderr'] = output.get('stderr', '')

        return jsonify({"message": "Command output received successfully"}), 200
    else:
        return jsonify({"message": "Invalid output format"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
