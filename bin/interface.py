#/usr/bin/env python

from dungeon_creator import Dungeon_Generator as dug
from ecs_systems import World
import json

#This is where we add functions that interface with the world object
#Things like, move_entity and whatnot
#Generate New World, Load World

class Interface:

	def __init__(self):
		pass

	def generate_dungeon(self):
		self.world = World()
		dg = dug(self.world)
		dg.create_dungeon(3)

	def load_dungeon(self):
		pass

	def save_dungeon(self):
		with open('data.json', 'w') as save_file:
			json.dump(self.world.WORLD, save_file, indent=4, sort_keys=True)

	def move_ent(self, eid): # eid will refer to the entity ID of entities.
		pass


	def get_ent_pos(self, eid):
		pass


	def get_ent_stats(self, eid):
		pass

z = Interface()
z.generate_dungeon()