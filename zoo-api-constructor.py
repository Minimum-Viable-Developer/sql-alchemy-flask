# TODO: https://marshmallow.readthedocs.io/en/stable/
# TODO: Use Constructors

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
from zoo_model import Specimen, Species, Genus, db_connect

app = Flask(__name__)
app.config['DEBUG'] = True

@app.route('/specimens', methods=['GET'])
def get_specimens():
    session = db_connect()
    specimens = session.query(Specimen).all()
    output_list = []
    for specimen in specimens:
        output_list.append(specimen.to_dict())
    return jsonify(output_list)


@app.route('/specimens', methods=['POST'])
def post_specimens():
    input_json = request.get_json()
    # print(input_json)
    if isinstance(input_json, list):
        for specimen in input_json:
            specimen = Specimen(specimen)
            print(specimen)
    else:
        return "Expecting list of specimens. Got {}".format(type(input_json))
    
    return "ok"


if __name__ == '__main__':
    app.run()
