from sqlalchemy import Integer, Column, String, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation

# For error handling
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound

import sys

Base = declarative_base()


# Genus is currently the "parent" of everything. It is the "root".
class Genus(Base):
    __tablename__ = 'genus'
    id = Column(Integer, primary_key=True)
    scientific_name = Column(String, unique=True)

    def __repr__(self):
        return "<Genus(common_name='%s')>" % (self.scientific_name)


# Species is a child of Genus
class Species(Base):
    __tablename__ = 'species'
    id = Column(Integer, primary_key=True)
    common_name = Column(String)
    scientific_name = Column(String, unique=True)
    # We define the relationship between Genus and Species here.
    genus = relation("Genus", backref="species")
    genus_id = Column(Integer, ForeignKey('genus.id'), nullable=False)

    def __repr__(self):
        return "<Species(common_name='%s')>" % (self.scientific_name)


class Specimen(Base):
    __tablename__ = 'specimen'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    birth_date_time = Column(Integer)
    # We define the relationship between Species and Specimen here.
    species = relation("Species", backref="specimen")
    species_id = Column(Integer, ForeignKey('species.id'))

    def __repr__(self):
        return "<Specimen(common_name='%s')>" % (self.name)


"""
This factory function will return any type of Class. We tell it what type of class we want with class_ name and give it some input data.
We use this "factory function" because we will need a LOT less code in our addSpecies() and addSpecimen() functions.
This function expects the following inputs:
session: The sqlalchemy database session.
data: A dict containing data we want to retreive or put in to the database
class_name: Which class do we want to instanciate? Genus, Species or Specimen?
Search key: When we try and get a record from the database, which key/column are we searching?

The output is a class instance. A record fetched from the database with session.query or one just added to the database with session.add.
"""
def classFactory(session, input_data, class_name, search_key):
    # Create a temporary referance to our class. Class could now be Genus, Species or Specimen
    class_ = getattr(sys.modules[__name__], class_name)
    try:
        # We see if there is already a record in the database. 
        # We use getattr because we are parameterising the instance variables. 
        # class_instance = session.query(Genus).filter(Genus.scientific_name == species_input["genus"]).one()
        class_instance = session.query(class_).filter(getattr(class_, search_key) == input_data[search_key]).one()
        print("Result Found")
        return class_instance
    except NoResultFound:  # Will Run if no record found in the database.
        print("No Result Found")
        class_instance = class_()  # Create a class instance        
        # Iterate over our input_data adding the data to the class instance. 
        # It is important that the keys in the dict match the class attributes.
        for key, value in input_data.items():
            print(key)
            setattr(class_instance, key, value)  # set the class attribute.
        session.add(class_instance)
        session.commit()
        return class_instance


def addSpecies(session, species_input):
    # Species_input should be a dict like:
    # {"common_name": "Domestic Cat", "scientific_name": "Felis catus", "genus": "Felis"}
    species_input["genus"] = classFactory(session, species_input["genus"], "Genus", "scientific_name")
    # species_input["genus"] has now been converted into a Genus class instance.
    species = classFactory(session, species_input, "Species", "scientific_name")


def addSpecimen(session, specimen_input):
    # specimen_input should be a dict like:
    # {"name": "bongo", "species": {"scientific_name": "Felis nigripes"}, "birth_date_time": "1262304000"}
    specimen_input["species"] = classFactory(session, specimen_input["species"], "Species", "scientific_name")
    # specimen_input["species"] has been converted to a Species class instance.
    specimen = classFactory(session, specimen_input, "Specimen", "name")


""" 
def addSpecimen(session, specimen_input):
    try:  # Lets check if we can retreive the species matching the specimen record.
        species = session.query(Species).filter(Species.scientific_name == specimen_input["scientific_species"]).one()
        try:  # We see if there is already a record in the database.
            print("#####START#####")
            print(specimen_input["name"])
            specimen = session.query(Specimen).filter(Specimen.name == specimen_input["name"]).one()
            print("Record for Specimen Found: " + specimen.name)
        except NoResultFound:  # Run if no record found in the database.
            print("Specimen not found in Database: Trying to insert record")
            specimen = Specimen()
            specimen.name = specimen_input["name"]
            specimen.birth_date_time = specimen_input["birth_date_time"]
            specimen.species = species
            session.add(specimen)
        session.commit()
    except NoResultFound: # We didn't find a matching species. Freak out.
        print("Fatal Error: Species not found in Database")
        exit()
    session.commit()
"""

if __name__ == "__main__":
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    import os
    # Delete the database that might already exist.
    try:
        os.remove("zoo.db")
    except:
        pass


    # Define a list of dicts of our species.
    species_list = [
        {"common_name": "Domestic Cat", "scientific_name": "Felis catus", "genus": {"scientific_name": "Felis"} },
        {"common_name": "Black Footed cat", "scientific_name": "Felis nigripes", "genus": {"scientific_name": "Felis"}},
        {"common_name": "Jungle cat", "scientific_name": "Felis chaus", "genus": {"scientific_name": "Felis"}},
        {"common_name": "Domestic Dog", "scientific_name": "Canis familiaris", "genus": {"scientific_name": "Canis"}},
        {"common_name": "Elk", "scientific_name": "Cervus canadensis", "genus": {"scientific_name": "Cervus"}},
        {"common_name": "Giant amoeba", "scientific_name": "Chaos carolinense", "genus": {"scientific_name": "Chaos"}},
        {"common_name": "Common Bottlenose Dolphin", "scientific_name": "Tursiops truncatus", "genus": {"scientific_name": "Tursiops"}},
        {"common_name": "Sea otter", "scientific_name": "Enhydra lutris", "genus": {"scientific_name": "Enhydra"}},
        {"common_name": "Wolf", "scientific_name": "Canis lupus", "genus": {"scientific_name": "Canis"}}
    ] 
    # Define a list of dicts of our specimens.
    specimen_list = [
        {"name": "bongo", "species": {"scientific_name": "Felis nigripes"}, "birth_date_time": "1262304000"},
        {"name": "coco", "species": {"scientific_name": "Cervus canadensis"}, "birth_date_time": "1293840000"},
        {"name": "lola", "species": {"scientific_name": "Tursiops truncatus"}, "birth_date_time": "1325376000"},
        {"name": "shadow", "species": {"scientific_name": "Tursiops truncatus"}, "birth_date_time": "1356998400"},
        {"name": "stella", "species": {"scientific_name": "Enhydra lutris"}, "birth_date_time": "1420070400"}
    ]

    # A bunch of stuff to make the connection to the database work.
    engine = create_engine('sqlite:///zoo2.db', echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Iterate over our list of dicts.
    for species in species_list:
        addSpecies(session, species)

    for specimen in specimen_list:
        addSpecimen(session, specimen)