
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from cityDB import AREA, Base, Neighborhood


engine = create_engine('sqlite:///city.db')


Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)


session = DBSession()



#gacan libaax area

Area3 = AREA(area_name="gacan libaax")
session.add(Area3)
session.commit()

nhood = Neighborhood(nhood_name="daami", description="old neighborhood",area_name=Area3.id )
session.add(nhood)
session.commit()

nhood1 = Neighborhood(nhood_name="newHargeisa", description="it have the biggeste masjid called masjid jaamac",area_name=Area3.id )
session.add(nhood1)
session.commit()

#ibrahim koodboor area
Area4 = AREA(area_name="ibrahim koodbuur")
session.add(Area4)
session.commit()


nhood = Neighborhood(nhood_name="jigjiga", description="it have also big market along the long road called jigjiga road",area_name=Area4.id )
session.add(nhood)
session.commit()

nhood = Neighborhood(nhood_name="mansoor area", description="called that name after one of the fomous hotels in Hargeisa Mansoor hotel", area_name=Area4.id )
session.add(nhood)
session.commit()



#ahmed dhagah area

Area2 = AREA(area_name="ahmed dhagah")
session.add(Area2)
session.commit()



nhood1 = Neighborhood(nhood_name="pepsi arae", description="named after one of the famous shop in that area,this area have the university of Hargeisa",
 area_name=Area2.id )


session.add(nhood1)
#session.rollback()
session.commit()

#26 june Area

Area1 = AREA(area_name="26June")

session.add(Area1)
session.commit()

nhood1 = Neighborhood(nhood_name="Goljanno", description="old neighborhood mostly middle class people, freindly place ",
	area_name=Area1.id)

session.add(nhood1)
#session.rollback()
session.commit()


nhood2 = Neighborhood(nhood_name="idacadda", description="also old neighborhood mostly middle class people, have  the largest\
vegtable market in the city, and it has also furniture market ",
	area_name=Area1.id)

session.add(nhood2)
session.commit()

nhood3 = Neighborhood(nhood_name="150ka", description="named after 150 streate in that area have both",
	area_name=Area1.id)

session.add(nhood3)
session.commit()

nhood4 = Neighborhood(nhood_name="hero awr", description="there is famous junction called hero awr and have the road with the same name",
	area_name=Area1.id)

session.add(nhood4)
session.commit()


print('items addedd succeed !')
