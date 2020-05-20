#TODO: https://marshmallow.readthedocs.io/en/stable/
#TODO: Use Constructors

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for

from sqlalchemy import Integer, Column, String, ForeignKey, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation


app = Flask(__name__)
app.config['DEBUG'] = True
Base = declarative_base()

class Genus(Base):
    __tablename__ = 'genus'
    id = Column(Integer, primary_key=True)
    scientific_name = Column(String, unique=True)

    def to_dict(self):
        output_dict = {}
        output_dict["scientific_name"] = self.scientific_name
        return output_dict

    def __repr__(self):
        return "<Genus(scientific_name='%s')>" % (self.scientific_name)


# Species is a child of Genus
class Species(Base):
    __tablename__ = 'species'
    id = Column(Integer, primary_key=True)
    common_name = Column(String)
    scientific_name = Column(String, unique=True)
    # We define the relationship between Genus and Species here.
    genus = relation("Genus", backref="species")
    genus_id = Column(Integer, ForeignKey('genus.id'), nullable=False)

    def get_genus(self, session, input_dict={}):
        if "scientific_name" in input_dict:
            self.genus = session.query(Genus).filter(Genus.scientific_name == input_dict["scientific_name"]).one()
        else:
            self.genus = session.query(Genus).filter(Genus.id == self.genus_id).one()
        return self.genus

    def to_dict(self):
        output_dict = {}
        output_dict["common_name"] = self.common_name
        output_dict["scientific_name"] = self.scientific_name
        output_dict["genus"] = self.genus.to_dict()
        return output_dict


    def __repr__(self):
        return "<Species(scientific_name='%s')>" % (self.scientific_name)


class Specimen(Base):
    __tablename__ = 'specimen'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    birth_date_time = Column(Integer)
    # We define the relationship between Species and Specimen here.
    species = relation("Species", backref="specimen")
    species_id = Column(Integer, ForeignKey('species.id'))

    def get_species(self, session, input_dict={}):
        if "scientific_name" in input_dict:
            self.species = session.query(Species).filter(Species.scientific_name == input_dict["scientific_name"]).one()
        else:
            self.species = session.query(Species).filter(Species.id == self.species_id).one()
        return self.species

    def to_dict(self):
        output_dict = {}
        output_dict["name"] = self.name
        output_dict["birth_date_time"] = self.birth_date_time
        output_dict["species"] = self.species.to_dict()
        return output_dict

    def __repr__(self):
        return "<Specimen(name='%s')>" % (self.name)


def db_connect():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    # A bunch of stuff to make the connection to the database work.
    engine = create_engine('sqlite:///zoo.db', echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


@app.route('/specimens', methods=['GET'])
def get_specimens():
    session = db_connect()
    specimens = session.query(Specimen).all()
    output_list = []
    for specimen in specimens:
        output_list.append(specimen.to_dict())
    return jsonify(output_list)


@app.route('/specimen', methods=['POST'])
def post_specimens():
    if request.method == 'POST':
        session = db_connect()
        input_specimen = request.get_json()
        specimen = Specimen()
        specimen.name = input_specimen["name"]
        specimen.birth_date_time = input_specimen["birth_date_time"]
        specimen.get_species(session, input_specimen["species"])
        session.add(specimen)
        session.commit()
        return jsonify(request.get_json())
    else:
        return "Unsupported Method"


if __name__ == '__main__':
    app.run()
