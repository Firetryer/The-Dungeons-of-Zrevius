

class MessageBoard():
	def __init__(self):
		self.message_queue = []
		self.observers = []
		
	def add_to_queue(self, message):
		self.message_queue.append(message)
		self.notify_observers(message)

	def register(self, observer):
		self.observers.append(observer)
		return observer 

	def notify_observers(self, message):
		for observer in self.observers:
			observer(message)


class Systems_Master:
	def __init__(self, game_master):
		self.world  	   = game_master.world
		self.WORLD   	   = game_master.world.WORLD
		self.message_board = game_master.message_board
		self.init_systems()

	def init_systems(self):
		# Create instances
		self.sys_generic   = Generic_System(self)
		self.sys_npc_ai    = NPC_Ai(self)
		self.sys_equipment = Equipment_Handling(self)

		# Register notification functions
		self.message_board.register(self.sys_generic.notified)
		self.message_board.register(self.sys_npc_ai.notified)
		self.message_board.register(self.sys_equipment.notified)


class Generic_System:
	def __init__(self, sys_master):
		self.world 		   = sys_master.world
		self.WORLD		   = sys_master.world.WORLD
		self.message_board = sys_master.message_board

	def movement(self, message):
		if message["type"] == "move":
			room_target = message['data']["room_target"]
			action_user = message['data']["action_user"]
			self.world.move_to_inventory(action_user, room_target)

	def drop(self, message):
		if message["type"] == "drop":
			item_target = message['data']["entity_id"]
			action_user = message['data']["action_user"]
			self.world.move_to_inventory(item_target, self.world.get_location(action_user))

	def pick_up(self, message):
		if message["type"] == "pick_up":
			item_target = message['data']["entity_id"]
			action_user = message['data']["action_user"]
			self.world.move_to_inventory(item_target, action_user)

	def notified(self, message):
		self.movement(message)
		self.pick_up(message)
		self.drop(message)


class NPC_Ai:
	def __init__(self, sys_master):
		self.world 		   = sys_master.world
		self.WORLD		   = sys_master.world.WORLD
		self.message_board = sys_master.message_board

	def ai_aggression_move(self, message):
		# If a new entity moves into a room, it checks if other entities in the room it moved into
		# can be aggressive to it.
		if message["type"] == "move":
			room_target = message['data']["room_target"]
			action_user = message['data']["action_user"]

			aggressive_entities = []
			aggressive_against_player = []
			# Get all entities that have aggressive component
			for entity in self.WORLD['inventory'][room_target]['items']:
				if self.world.has_components(entity, ['aggressive']):
					aggressive_entities.append(entity)

			for entity in aggressive_entities:
				if self.WORLD['aggressive'][entity]['against'] == "player":
					aggressive_against_player.append(entity) 

	def notified(self, message):
		self.ai_aggression_move(message)

# This isn't really a system on its own, just a helper for generic systems

class Equipment_Handling:
	def __init__(self, sys_master):
		self.world 		   = sys_master.world
		self.WORLD		   = sys_master.world.WORLD
		self.message_board = sys_master.message_board

	def notified(self, message):
		self.equip(message)
		self.unequip(message)

	def unequip(self, message):
		if message["type"] == "unequip":
			item    = message['data']["entity_id"]
			slot = self.WORLD['equippable'][item]['equipped_slot']
			by   = self.WORLD['equippable'][item]['equipped_by']
			self._unequip(by, slot)

	def equip(self, message):
		if message["type"] == "equip":
			item_id    = message['data']["entity_id"]
			ent_id    = message['data']["action_user"]
			slot = message['data']["slot"]

			entity_equipment = self.WORLD['equipment'][ent_id]

			if slot == "dual_wield":
				if entity_equipment['left_hand'] == None and entity_equipment['right_hand'] == None:
					self._equip(ent_id, item_id, slot)
				else: 
					self._unequip(ent_id, 'left_hand')
					self._unequip(ent_id, 'right_hand')
					self._equip(ent_id, item_id, slot)
			elif slot == "left_hand":
				if entity_equipment['left_hand'] == None:
					self._equip(ent_id, item_id, slot)
				else:
					self._unequip(ent_id, 'left_hand')
					self._equip(ent_id, item_id, slot)
			elif slot == "right_hand":
				if entity_equipment['right_hand'] == None:
					self._equip(ent_id, item_id, slot)
				else:
					self._unequip(ent_id, 'right_hand')
					self._equip(ent_id, item_id, slot)

	def _equip(self, ent_id, item_id, slot):
		self.WORLD['inventory'][ent_id]['items'].remove(item_id)
		self.WORLD['equipment'][ent_id][slot] = item_id
		self.WORLD['equippable'][item_id]['equipped_by']   = ent_id
		self.WORLD['equippable'][item_id]['equipped_slot'] = slot
		message = {
			"type" : "notification",
			"data"  : {
				"action" 	 : "equip",
				"action_user": ent_id,
				"item_id"	 : item_id
			}
		}
		self.message_board.add_to_queue(message)

	def _unequip(self, ent_id, slot):
		if self.WORLD['equipment'][ent_id][slot] != None:
			item_id = self.WORLD['equipment'][ent_id][slot]
			self.WORLD['equipment'][ent_id][slot] = None
			self.WORLD['inventory'][ent_id]['items'].append(item_id)
			message = {
				"type" : "notification",
				"data"  : {
					"action" 	 : "unequip",
					"action_user": ent_id,
					"item_id"	 : item_id
				}
			}
			self.message_board.add_to_queue(message)




	
