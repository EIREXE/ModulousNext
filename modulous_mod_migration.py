from SpaceDock.objects import *
from SpaceDock.database import *

for modv in ModVersion.query:
    #modv.gameversion_id = GameVersion.query.filter(GameVersion.id==modv.mod.game.version[0].id).first().id
    print(modv.gameversion)
    db.add(modv)

db.commit()
