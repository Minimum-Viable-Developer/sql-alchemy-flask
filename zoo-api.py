
from flask import Flask, flash, jsonify, redirect, render_template, request, url_for

from sqlalchemy import Integer, Column, String, ForeignKey, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation


app = Flask(__name__)
app.config['DEBUG'] = True
Base = declarative_base()

# Genus is currently the "parent" of everything. It is the "root".
class Genus(Base):
    __tablename__ = 'genus'
    id = Column(Integer, primary_key=True)
    scientific_name = Column(String)

    def __repr__(self):
        return "<Genus(common_name='%s')>" % (self.scientific_name)


# Species is a child of Genus
class Species(Base):
    __tablename__ = 'species'
    id = Column(Integer, primary_key=True)
    common_name = Column(String)
    scientific_name = Column(String)
    # We define the relationship between Genus and Species here.
    genus = relation("Genus", backref="species")
    genus_id = Column(Integer, ForeignKey('genus.id'), nullable=False)

    def __repr__(self):
        return "<Species(common_name='%s')>" % (self.scientific_name)


class Specimen(Base):
    
    __tablename__ = 'specimen'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    birth_date_time = Column(Integer)
    # We define the relationship between Species and Specimen here.
    species = relation("Species", backref="specimen")
    species_id = Column(Integer, ForeignKey('species.id'))

    def __repr__(self):
        return "<Specimen(common_name='%s')>" % (self.name)

'''
class Enclousure(Base):
    __tablename__ = 'enclosure'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    # We define the relationship between Species and Specimen here.
    species = relation("Species", backref="specimen")
    species_id = Column(Integer, ForeignKey('species.id'))

    def __repr__(self):
        return "<Specimen(common_name='%s')>" % (self.name)
'''

def db_connect():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    # A bunch of stuff to make the connection to the database work.
    engine = create_engine('sqlite:///zoo.db', echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


@app.route('/genus/<search_term>', methods=['GET'])
def get_genus(search_term):
    if request.method == 'GET':
        return_list = []
        session = db_connect()
        print(search_term)
        for row in session.query(Genus).filter(Genus.id == search_term).all():
            row_dict = row.__dict__
            row_dict.pop("_sa_instance_state")
            return_list.append(row_dict)
        return jsonify(return_list)
    else:
        return "Unsupported Method"


@app.route('/genus_and_species/<search_term>', methods=['GET'])
def get_genus_and_species(search_term):
    if request.method == 'GET':
        return_list = []
        session = db_connect()
        print(search_term)
        for genus, species in session.query(Genus, Species).filter(
            Genus.id == search_term, 
            Genus.id == Species.genus_id).all():
            row = {} 
            row["genus_id"] = genus.id
            row["genus_scientific_name"] = genus.scientific_name
            row["species_id"] = species.id
            row["species_scientific_name"] = species.scientific_name
            return_list.append(row)
        return jsonify(return_list)
    else:
        return "Unsupported Method"



@app.route('/genus_and_species_and_specimen/<search_term>', methods=['GET'])
def get_genus_and_species_and_specimen(search_term):
    if request.method == 'GET':
        return_list = []
        session = db_connect()
        print(search_term)
        for genus, species, specimen in session.query(
            Genus, Species, Specimen
            ).filter(
            Genus.id == search_term, 
            Genus.id == Species.genus_id, 
            Species.id == Specimen.species_id
            ).all():
            row = {} 
            row["genus_id"] = genus.id
            row["genus_scientific_name"] = genus.scientific_name
            row["species_id"] = species.id
            row["species_scientific_name"] = species.scientific_name
            row["specimen_id"] = specimen.id
            row["specimen_name"] = specimen.name
            return_list.append(row)
        return jsonify(return_list)
    else:
        return "Unsupported Method"


@app.route('/specimen_and_species_and_genus/<search_term>', methods=['GET'])
def get_specimen_and_species_and_genus(search_term):
    if request.method == 'GET':
        return_list = []
        session = db_connect()
        print(search_term)
        for genus, species, specimen in session.query(
            Genus, Species, Specimen
            ).filter(
            Specimen.id == search_term, 
            Genus.id == Species.genus_id, 
            Species.id == Specimen.species_id
            ).all():
            row = {} 
            row["genus_id"] = genus.id
            row["genus_scientific_name"] = genus.scientific_name
            row["species_id"] = species.id
            row["species_scientific_name"] = species.scientific_name
            row["specimen_id"] = specimen.id
            row["specimen_name"] = specimen.name
            return_list.append(row)
        return jsonify(return_list)
    else:
        return "Unsupported Method"


@app.route('/genus', methods=['POST'])
def genus_post():
    if request.method == 'POST':
        session = db_connect()
        input_genus = request.get_json()
        genus = Genus()
        genus.scientific_name = input_genus["scientific_name"]
        session.add(genus)
        session.commit()
        return jsonify(request.get_json())
    else:
        return "Unsupported Method"


@app.route('/json')
def show_json():
    return_list = []
    session = db_connect()
    for row in session.query(Genus).all():
        row_dict = row.__dict__
        row_dict.pop("_sa_instance_state")
        print(row_dict)
        return_list.append(row_dict)
    return jsonify(return_list)


if __name__ == '__main__':
    app.run()
