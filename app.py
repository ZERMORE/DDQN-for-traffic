from flask import Flask, request, jsonify, render_template
import subprocess
import uuid
import os

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/run-model', methods=['POST'])
def run_model():
    try:
        data = request.json
        lane1 = data['lane1']
        lane2 = data['lane2']
        lane3 = data['lane3']

        unique_id = uuid.uuid4()
        directory = f'run_{unique_id}'
        os.makedirs(directory, exist_ok=True)

        route_filename = os.path.join(directory, 'flow.rou.xml')
        sumocfg_filename = os.path.join(directory, 'config.sumocfg')

        with open(route_filename, 'w', encoding='utf-8') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write("<routes>\n")
            f.write(
                '    <vType id="ACCType" color="22,255,255" length="5.0" carFollowModel="IDM" laneChangeModel="LC2013" lcSpeedGain="1"/>\n')
            f.write(
                '    <vType id="CACCType" color="22,55,255" length="5.0" carFollowModel="IDM" laneChangeModel="LC2013" lcSpeedGain="1"/>\n')
            f.write(
                '    <vType id="standard_car" color="255,225,0" length="5.0" maxSpeed="22.2" carFollowModel="IDM" laneChangeModel="LC2013" speedFactor="normc(1,0.1,0.2,2)" lcSpeedGain="1"/>\n')
            f.write('    <route id="0" edges="R1 R2 R3 R4 R5"/>\n')
            f.write('    <route id="1" edges="R1 R2 R3 R4 RL3"/>\n')
            f.write('    <route id="2" edges="L1 RL1 RL2 R3 R4 R5"/>\n')
            f.write('    <!-- Vehicles, persons and containers (sorted by depart) -->\n')
            f.write(
                f'    <flow id="f_3" begin="1.00" departLane="free" departPos="free" departSpeed="speedLimit" route="0" end="7200.00" vehsPerHour="{lane1}.00"/>\n')
            f.write(
                f'    <flow id="f_1" begin="1.00" departLane="free" departPos="free" departSpeed="speedLimit" route="1" end="7200.00" vehsPerHour="{lane2}.00"/>\n')
            f.write(
                f'    <flow id="f_2" begin="1" departLane="free" departPos="free" departSpeed="speedLimit" route="2" end="7200.00" vehsPerHour="{lane3}.00"/>\n')
            f.write("</routes>\n")
            
        with open(sumocfg_filename, 'w', encoding='utf-8') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<configuration>\n')
            f.write('    <input>\n')
            f.write(f'        <net-file value="D:\项目文件\人工智能创意赛\webUI\wuhandata\\map2.net.xml"/>\n')
            f.write(f'        <route-files value="flow.rou.xml"/>\n')
            f.write('        <additional-files value="D:\项目文件\人工智能创意赛\webUI\wuhandata\\nsdet.add.xml"/>\n')
            f.write('    </input>\n')
            f.write('    <time>\n')
            f.write('        <begin value="0"/>\n')
            f.write('        <end value="10000"/>\n')
            f.write('        <step-length value="1"/>\n')
            f.write('    </time>\n')
            f.write('</configuration>\n')

        result = subprocess.run(['python', 'model.py', sumocfg_filename], capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(f"Model script failed with error: {result.stderr}")

        output_dir = os.path.join(directory, 'output')
        if not os.path.exists(output_dir):
            raise FileNotFoundError(f"Output folder {output_dir} was not created.")
        output_path = os.path.join(output_dir, 'output.txt')
        if os.path.exists(output_path):
            with open(output_path, 'r', encoding='utf-8') as f:
                model_output = f.read()
            return jsonify({"output": model_output})
        else:
            return jsonify({"output": "Model ran successfully but no output found."})

    except Exception as e:
        app.logger.error(f"Error running model: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
