from sqlalchemy import Integer, Column, String, ForeignKey, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation

Base = declarative_base()

class Genus(Base):
    __tablename__ = 'genus'
    id = Column(Integer, primary_key=True)
    scientific_name = Column(String, unique=True)

    def __init__(self, input_dict, session=None):
        new_session = False
        if session is None:
            session = db_connect()
            new_session = True
        self.scientific_name = input_dict["scientific_name"]
        if new_session:
            print("new session in Genus, commiting and closing")
            session.commit()
            

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


    def __init__(self, input_dict, session=None):
        new_session = False
        if session is None:
            session = db_connect()
            new_session = True
        self.scientific_name = input_dict["scientific_name"]
        self.common_name = input_dict["common_name"]
        genus_ = input_dict["genus"]
        if isinstance(genus_, dict):
            try:
                self.genus = session.query(Genus).filter(Genus.scientific_name == genus_["scientific_name"]).one()
            except:
                self.genus = Genus(input_dict["genus"], session=session)
        if isinstance(genus_, Genus):
            self.genus = genus_
        if new_session:
            print("new session in Species, commiting and closing")
            session.commit()


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

    def __init__(self, input_dict, session=None):
        new_session = False
        if session is None:
            session = db_connect()
            new_session = True
        self.name = input_dict["name"]
        self.birth_date_time = input_dict["birth_date_time"]
        species_ = input_dict["species"]
        if isinstance(species_, dict):
            try:
                self.species = session.query(Species).filter(Species.scientific_name == species_["scientific_name"]).one()
            except:
                self.species = Species(input_dict["species"], session=session)
        if isinstance(species_, Species):
                self.species = species_
        if new_session:
            print(self.to_dict())
            print("new session in Specimen, commiting and closing")
            session.commit()

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
    engine = create_engine('sqlite:///zoo2.db', echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()