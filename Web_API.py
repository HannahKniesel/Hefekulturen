import argparse
import pandas as pd
import json
import base64
import cv2
from flask import Flask, request, jsonify
from Utils import setup_layout, open_image, compute_grid
from Evaluation import evaluate
from Variables import MIN_COLONY_SIZE, P_VALUE_NULLHYPOTHESIS, USE_HARD_GRID

app = Flask(__name__)

def encode_image(image):
    _, buffer = cv2.imencode('.png', image)
    return base64.b64encode(buffer).decode('utf-8')

def process_plates(reference_plate_path, experiment_plate_path):
    print(f"Processing reference plate: {reference_plate_path}\nProcessing experiment plate: {experiment_plate_path}")

    # Setup master plate layout
    x_expected, y_expected, layout_names = setup_layout(reference_plate_path)

    # Load and preprocess images
    reference_plate = open_image(reference_plate_path)
    experiment_plate = open_image(experiment_plate_path)

    if reference_plate is None:
        raise ValueError(f"Cannot open reference plate image: {reference_plate_path}")
    if experiment_plate is None:
        raise ValueError(f"Cannot open experiment plate image: {experiment_plate_path}")

    rgb_grid_reference, sizes_reference, x_start, x_end, y_start, y_end = compute_grid(
        reference_plate, x_expected, y_expected, USE_HARD_GRID, plot=False
    )

    rgb_grid_experiment, sizes_experiment, _, _, _, _ = compute_grid(
        experiment_plate, x_expected, y_expected, USE_HARD_GRID, plot=False
    )

    # Evaluate
    quadruples, minimum_size, reference_plate, experiment_plate, normalized_plate, highlights_absolute, highlights, highlights_both = evaluate(
        experiment_plate,
        reference_plate,
        sizes_experiment,
        sizes_reference,
        x_start,
        x_end,
        y_start,
        y_end,
        layout_names,
        MIN_COLONY_SIZE,
        P_VALUE_NULLHYPOTHESIS
    )

    # Retrieve data
    data = {
        'Position': [f"{quad.position[1]} {quad.position[0]}" for quad in quadruples],
        'Name': [str(quad.name) for quad in quadruples],
        'Exp1: Significant Size': ["yes" if quad.absolute_size > minimum_size else "no" for quad in quadruples],
        'Exp1: Absolute Size': [quad.absolute_size for quad in quadruples],
        'Exp1: Minimum Threshold': [minimum_size for _ in quadruples],

        'Exp2: Significant Difference': ["yes" if quad.p_value < P_VALUE_NULLHYPOTHESIS else "no" for quad in quadruples],
        'Exp2: P-Value': [quad.p_value for quad in quadruples],
        'Exp2: Effect Size': [quad.effect_size for quad in quadruples],
        'Exp2: Growth Factor': [quad.growthfactor for quad in quadruples],

        'Is Valid': ["valid" if quad.is_valid else "invalid" for quad in quadruples],
        'Reason': [quad.reason for quad in quadruples],
        'Bigger Row': [quad.bigger_row for quad in quadruples],

        **{f"A{i+1} Normalized": [str(quad.quadrupelA.sizes[i]) for quad in quadruples] for i in range(4)},
        **{f"B{i+1} Normalized": [str(quad.quadrupelB.sizes[i]) for quad in quadruples] for i in range(4)},

        **{f"A{i+1} Raw Experiment": [str(quad.quadrupelA.sizes_exp[i]) for quad in quadruples] for i in range(4)},
        **{f"B{i+1} Raw Experiment": [str(quad.quadrupelB.sizes_exp[i]) for quad in quadruples] for i in range(4)},

        **{f"A{i+1} Raw Reference": [str(quad.quadrupelA.sizes_ref[i]) for quad in quadruples] for i in range(4)},
        **{f"B{i+1} Raw Reference": [str(quad.quadrupelB.sizes_ref[i]) for quad in quadruples] for i in range(4)},
    }

    # Encode images
    images = {
        'reference_plate': encode_image(reference_plate),
        'experiment_plate': encode_image(experiment_plate),
        'normalized_plate': encode_image(normalized_plate),
        'highlights_absolute': encode_image(highlights_absolute),
        'highlights_difference': encode_image(highlights),
        'highlights_both': encode_image(highlights_both),
    }

    return {
        'data': data,
        'images': images
    }

@app.route('/process', methods=['POST'])
def process_request():
    request_data = request.json
    reference_path = request_data.get('reference')
    experiment_path = request_data.get('experiment')

    if not reference_path or not experiment_path:
        return jsonify({"error": "Both 'reference' and 'experiment' paths are required."}), 400

    try:
        result = process_plates(reference_path, experiment_path)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the plate processing web API.")
    parser.add_argument("--host", default="0.0.0.0", help="Host for the web server.")
    parser.add_argument("--port", type=int, default=5000, help="Port for the web server.")

    args = parser.parse_args()
    app.run(host=args.host, port=args.port)
