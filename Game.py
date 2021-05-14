import pygame
import random
import math

from pygame.locals import *

pygame.init()
pygame.font.init()



FPS = 60

clock = pygame.time.Clock()
deltaTime = 0

font = pygame.font.SysFont("Times New Roman", 20)

screen = pygame.display.set_mode((600, 500))

scroll = [0, 0]

coins = 100

class ButtonTXT():
	
	WHITE = (255, 255, 255)
	BLACK = (0, 0, 0)

	font = pygame.font.SysFont("Times New Roman", 20)

	def __init__(self, window, x, y, text, border = True, width = 100, height = 40, col = (50, 50, 50), hover_col = (100, 100, 100), click_col = (255, 255, 255), text_col = WHITE):
		self.window = window
		self.x = x
		self.y = y
		self.text = text
		self.col = col
		self.hover_col = hover_col 
		self.click_col = click_col
		self.text_col = text_col
		self.width = width
		self.height = height
		self.clicked = False
		self.border = border

	def set_text(self, newText):
		self.text = newText


	def draw(self, window):
		
		action = False

		pos = pygame.mouse.get_pos()

		button_rect = pygame.Rect(self.x, self.y, self.width, self.height)

		if button_rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1:
				self.clicked = True
				pygame.draw.rect(self.window, self.click_col, button_rect)
			elif pygame.mouse.get_pressed()[0] == 0 and self.clicked == True:
				self.clicked = False
				action = True
			else:
				pygame.draw.rect(self.window, self.hover_col, button_rect)
		else:
			pygame.draw.rect(self.window, self.col, button_rect)

		if self.border:
			pygame.draw.line(self.window, self.WHITE, (self.x, self.y), (self.x + self.width, self.y), 2)
			pygame.draw.line(self.window, self.WHITE, (self.x, self.y), (self.x, self.y + self.height), 2)
			pygame.draw.line(self.window, self.BLACK, (self.x + self.width, self.y), (self.x + self.width, self.y + self.height), 2)
			pygame.draw.line(self.window, self.BLACK, (self.x, self.y + self.height), (self.x + self.width, self.y + self.height), 2)

		text_img = self.font.render(self.text, True, self.text_col)
		self.window.blit(text_img, (self.x + int(self.width / 2) - int(text_img.get_width() / 2), self.y + int(self.height / 2) - int(text_img.get_height() // 2)))
		return action




class Bullet():
	def __init__(self, x, y, damage, target):
		self.x = x
		self.y = y
		self.damage = damage
		self.target = target
		self.speed = 2
		self.hitbox = pygame.Rect(self.x, self.y, 5, 5)

	def ai(self):
		mag = math.sqrt((self.target.x - self.x) * (self.target.x - self.x) + (self.target.y - self.y) * (self.target.y - self.y))
		xDir = (self.target.x - self.x) / mag
		
		yDir = (self.target.y - self.y) / mag
		
		return self.move(xDir, yDir)

	def move(self, xDir, yDir):

		self.x += xDir * self.speed
		self.y += yDir * self.speed
		self.hitbox = pygame.Rect(self.x, self.y, 5, 5)
		if self.hitbox.colliderect(self.target.hitbox):
			#print("colliding")
			self.target.takeDamage(self.damage)
			return True
		else:
			return False

	def draw(self):
		pygame.draw.rect(screen, (255, 0, 0), (self.x - scroll[0], self.y - scroll[1], 5, 5))

class Tower():
	def __init__(self, x, y):
		self.x = x
		self.displayX = x
		self.y = y
		self.displayY = y
		self.level = 0
		self.damage = 0
		self.health = 0
		self.range = 22
		self.cost = 100
		self.size = (20, 20)
		self.hitbox = pygame.Rect((self.x, self.y), self.size)
		self.selected = False
		self.canShoot = True
		self.ReloadTime = 500
		self.shotTime = pygame.time.get_ticks()
		self.upgradeButton = ButtonTXT(screen, 0, 0, "Upgrade", False)
		self.myBullets = []
		self.MaxAmmo = 10
		self.ammo = 10
		self.ammoInRoute = 0
		self.potentialAmmo = self.ammo + self.ammoInRoute


	def ai(self, zombies):

		if self.shotTime + self.ReloadTime < pygame.time.get_ticks() and self.ammo > 0:
			self.canShoot = True

		if self.canShoot:
			self.shoot(zombies)
			


	def shoot(self, zombies):
		
		for z in zombies:
				distSquared = (z.x -( self.x + self.hitbox.w // 2)) *  (z.x -( self.x + self.hitbox.w // 2)) + (z.y -(self.y + self.hitbox.h // 2)) * (z.y -(self.y + self.hitbox.h // 2))				
				if distSquared < self.range * self.range and self.canShoot:
					self.canShoot = False
					self.ammo -= 1
					self.potentialAmmo = self.ammo + self.ammoInRoute
					self.shotTime = pygame.time.get_ticks()
					self.myBullets.append(Bullet(self.x + self.hitbox.w // 2, self.y + self.hitbox.h // 2, self.damage, z))

	def addAmmo(self, amount):
		self.ammo += amount
		self.ammoInRoute -= amount
		self.potentialAmmo = self.ammo + self.ammoInRoute
		if self.ammo > self.MaxAmmo:
			self.ammo = self.MaxAmmo

	def levelUp(self):
		print("level up")
		self.level += 1
		self.damage = 14 * self.level
		self.health = 200 * self.level
		self.range = 100 + 5 * self.level
		self.cost = 200 + 10 * self.level * self.level
		self.MaxAmmo = 10 * self.level

	def update(self, zombies):
		self.displayX = self.x - scroll[0]
		self.displayY = self.y - scroll[1]
		self.hitbox = pygame.Rect((self.displayX, self.displayY), self.size)
		self.ai(zombies)
		remove = []
		global coins
		for b in self.myBullets:
			b.draw()
			if b.ai():
				remove.append(b)
				coins += 10

		

		for b in remove:
			self.myBullets.remove(b)
			

	def draw(self, zombies):
		
		surf = pygame.Surface((self.range * 3, self.range * 3))


		if self.selected:
			pygame.draw.circle(surf, (20, 20, 20), (self.range + self.hitbox.w // 2, self.range + self.hitbox.h // 2) , self.range)
			pygame.draw.rect(surf, (0, 0, 255), (self.range - 2, self.range - 2, self.size[0] + 4, self.size[1] + 4))
		pygame.draw.rect(surf, (255, 255, 0), ((self.range, self.range), (self.hitbox.w, self.hitbox.h)))
		pygame.draw.rect(surf, (0, 255, 0), ((self.range, self.range), (self.hitbox.w // 2, self.hitbox.h * self.ammo / self.MaxAmmo)))
		surf.convert_alpha()
		surf.set_colorkey((0, 0, 0))
		screen.blit(surf, (self.hitbox.x - self.range, self.hitbox.y - self.range), special_flags = BLEND_RGB_ADD)
		self.update(zombies)

class Base():
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.size = (30, 30)
		self.level = 1
		self.health = 100
		self.hitbox = pygame.Rect((self.x, self.y), self.size)

	def update(self):
		self.hitbox = pygame.Rect((self.x - scroll[0], self.y - scroll[1]), self.size)
		if self.health <= 0:
			print("Game Over")


	def draw(self):
		self.update()
		
		pygame.draw.rect(screen, (0, 0, 255), self.hitbox)

class Unit():
	def __init__(self, x, y, ai, base, color = (0, 0, 255), health = 100, speed = 1, damage = 10, target = None, towers = []):
		self.x = x
		self.y = y
		self.health = health
		self.alive = True
		self.aiFunc = ai
		self.speed = speed
		self.damage = damage
		self.color = color
		self.hitbox = pygame.Rect(self.x - 5, self.y - 5, 10, 10)
		self.target = target
		self.towers = towers
		self.base = base
		self.hasAmmo = False
		self.carryCapacity = 10
	#	self.moveUp = False
	#	self.moveDown = False
	#	self.moveLeft = False
	#	self.moveRight = False




	def meleeAttack(self):
		pass

	def rangeAttack(self):
		pass

	def attack(self, attack):
		self.attack()

	def deadCheck(self):
		if self.health <= 0:
			self.alive = False
		
		return self.alive

	def move(self, xDir, yDir):
		self.x += xDir * self.speed
		self.y += yDir * self.speed

	def ai(self):
		return self.aiFunc(self)
		
	def workerAI(self):
		if self.alive:
			if self.target:
				dist = math.sqrt((self.target.x - self.x) * (self.target.x - self.x) + (self.target.y - self.y) * (self.target.y - self.y))
				if dist == 0:
					dist = 1
				xDir = (self.target.x - self.x) / dist
				yDir = (self.target.y - self.y) / dist
				self.move(xDir, yDir)
				if self.hitbox.collidepoint((self.target.x, self.target.y)):
					

					if self.target == self.base:
						self.hasAmmo = True
					else:
						self.hasAmmo = False
						self.target.addAmmo(self.carryCapacity)
					self.target = None
			else:
				if self.hasAmmo:
					
					lowestAmmo = 10000
					newTarget = None
					for t in self.towers:
						if t.potentialAmmo / t.MaxAmmo <= lowestAmmo:
							lowestAmmo = t.potentialAmmo / t.MaxAmmo
							newTarget = t

					if newTarget:
						
						self.target = newTarget
						self.target.ammoInRoute += self.carryCapacity
				else:
					self.target = self.base

			




			return True
		else:
			return False



	def zombieAI(self):
		if self.alive:
			if self.target:
				dist = math.sqrt((self.target.x - self.x) * (self.target.x - self.x) + (self.target.y - self.y) * (self.target.y - self.y))
				xDir = (self.target.x - self.x) / dist
				yDir = (self.target.y - self.y) / dist
			else:
				# todo: grab the nearest tower and start to destroy it
				xDir = random.random() - .5
				yDir = random.random() - .5

			self.move(xDir, yDir)


			if self.hitbox.collidepoint((self.target.x, self.target.y)):
				self.target.health -= self.damage

		return self.alive

	def takeDamage(self, amount):
		self.health -= amount
		self.deadCheck() #do something if dead ????

	def heal(self, amount):
		self.health += amount


	def update(self):
		self.hitbox = pygame.Rect(self.x - 5, self.y - 5, 10, 10)

	def draw(self):
		self.update()
		pygame.draw.circle(screen, self.color, (self.x - scroll[0], self.y - scroll[1]), 5)


class Spawner():

	def __init__(self, x, y, zombies, base):
		self.x = x
		self.y = y
		self.spawnPoints = []
		for i in range(20):
			xDir = random.random() * 2 - 1
			yDir = random.random() * 2 - 1
			mag = math.sqrt((xDir * xDir) + (yDir * yDir))
			xDir = xDir / mag
			yDir = yDir / mag

			self.spawnPoints.append([xDir * 500, yDir * 600])

		
		self.zombies = zombies
		self.cooldown = 1000
		self.spawnCountdown = self.cooldown
		self.wave = 0
		self.NumZombiesToSpawn = 1
		self.waveCooldown = 1000
		self.waveCountdown = 500
		self.endOfWave = pygame.time.get_ticks()
		self.state = 0 #spawning = -1 waiting = 0 counting = 1
		self.zombieTarget = base

	def spawnZombie(self):
		spawnPoint = random.choice(self.spawnPoints)
		self.zombies.append(Unit(spawnPoint[0], spawnPoint[1], Unit.zombieAI, self.zombieTarget, (0, 255, 0) , self.wave * self.wave, 1, self.wave * 1.1, self.zombieTarget))
		self.lastSpawnTime = pygame.time.get_ticks()
		self.NumZombiesToSpawn -= 1
		
	


	def update(self, deltaTime):

		if self.state == 0:
			if self.waveCountdown <= 0:
				if len(self.zombies) == 0:
					self.state = -1
					self.wave += 1
					print(self.wave)
					self.NumZombiesToSpawn = self.wave * 20 * self.wave
					#self.endOfWave = pygame.time.get_ticks()
			else:
				self.waveCountdown = self.waveCountdown - deltaTime


		if self.state == -1:
			if self.spawnCountdown <= 0:
				self.spawnZombie()
				self.spawnCountdown = self.cooldown
				if self.NumZombiesToSpawn <= 0:
					self.state = 0
					self.waveCountdown = self.waveCooldown
			else:
				self.spawnCountdown -= deltaTime






def main():
	

	towers = []
	zombies = []
	workers = []
	base = Base(210, 210)
	spawner1 = Spawner(-59, -39, zombies, base)


	#towers.append(Tower(50, 50))
	#zombies.append(Unit(100, 50))
	

	clicked = False
	right_clicked = False
	selectedTower = None

	run = True

	start_drag_pos = None
	end_drag_pos = None
	build_pos = None


	build_button = ButtonTXT(screen, 0, 80, "Build Tower", False)
	buy_worker_button = ButtonTXT(screen, 0, 120, "Buy Worker", False)
	deselect_button = ButtonTXT(screen, 0, 40, "Deselect", False)

	global scroll
	prev_scroll = scroll

	global coins



	while run:

		deltaTime = clock.tick(30)
		#print(deltaTime)
		screen.fill((0, 0, 0))

		panel = pygame.Rect(0, 0, 100, 500)
		
		

		for event in pygame.event.get():
			if event.type == QUIT:
				run = False

		
		if pygame.mouse.get_pressed()[0] == 1:
			clicked = True
			if not panel.collidepoint(pygame.mouse.get_pos()):
				build_pos = pygame.mouse.get_pos()
		else:
			clicked = False		


	#	if pygame.mouse.get_pressed()[2] == 1 and right_clicked == False:
	#		start_drag_pos = pygame.mouse.get_pos()
	#		right_clicked = True
	#	elif pygame.mouse.get_pressed()[2] == 0 and right_clicked:
	#		right_clicked = False
	#		end_drag_pos = pygame.mouse.get_pos()

		if pygame.mouse.get_pressed()[2] == 1 and not start_drag_pos:
			start_drag_pos = pygame.mouse.get_pos()
		elif pygame.mouse.get_pressed()[2] == 1 and start_drag_pos:
			end_drag_pos = pygame.mouse.get_pos()
		
		if end_drag_pos:


		
			
			#print(start_drag_pos)
			#print(end_drag_pos)
			temp_scroll = (end_drag_pos[0] - start_drag_pos[0] , end_drag_pos[1] - start_drag_pos[1])
			scroll = (prev_scroll[0] + temp_scroll[0], prev_scroll[1] + temp_scroll[1])

			
			#print(scroll)
		if pygame.mouse.get_pressed()[2] == 0 and end_drag_pos:
			prev_scroll = scroll
			start_drag_pos = None
			end_drag_pos = None

		pos = pygame.mouse.get_pos()
		if clicked:			

			for t in towers:
				if t.hitbox.collidepoint(pos):
					t.selected = True
				else:
					t.selected = False


		for t in towers:
			if t.selected:
				selectedTower = t
			t.draw(zombies)
		remove = []
		for z in zombies:
			if z.ai():
				z.draw()
			else:
				remove.append(z)

		for z in remove:
			zombies.remove(z)

		remove = []
		for w in workers:
			if w.ai():
				w.draw()
			else:
				remove.append(w)

		for w in remove:
			workers.remove(w)

		base.draw()
		spawner1.update(deltaTime)
		
		pygame.draw.rect(screen, (100, 100, 100), panel)

		if selectedTower:
			if selectedTower.upgradeButton.draw(screen):
				if coins - selectedTower.cost >= 0:
					coins -= selectedTower.cost
					selectedTower.levelUp()
					selectedTower = None
		
		if build_pos and not selectedTower:
			pygame.draw.circle(screen, (0, 0, 255), (build_pos[0], build_pos[1]), 10)
			if build_button.draw(screen):
				towers.append(Tower(build_pos[0] + scroll[0], build_pos[1] + scroll[1]))


		if buy_worker_button.draw(screen):
			if coins >= len(workers):
				coins -= len(workers)
				workers.append(Unit(base.x, base.y, Unit.workerAI, base, (255, 255, 255), towers = towers))


		#print(scroll)	
		text_img = font.render("Coins : " + str(coins), True, (255, 255, 255))
		screen.blit(text_img, (50 - int(text_img.get_width() / 2), 400 - int(text_img.get_height() // 2)))

		if deselect_button.draw(screen):
			selectedTower = None

		pygame.display.update()




if __name__ == "__main__":
	main()