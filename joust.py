#Joust by S Paget

import pygame, random
pygame.mixer.pre_init(44100,-16,2,512) 
pygame.init() 

GRAVITY = 0.5

def load_sliced_sprites(w, h, filename):
     #returns a list of image frames sliced from file
     images = []
     master_image = pygame.image.load( filename )
     master_image = master_image.convert_alpha()
     master_width, master_height = master_image.get_size()
     for i in range(int(master_width/w)):
          images.append(master_image.subsurface((i*w,0,w,h)))
     return images

def loadPlatforms():
     platformimages = []
     platformimages.append(pygame.image.load("plat1.png"))
     platformimages.append(pygame.image.load("plat2.png"))
     platformimages.append(pygame.image.load("plat3.png"))
     platformimages.append(pygame.image.load("plat4.png"))
     platformimages.append(pygame.image.load("plat5.png"))
     platformimages.append(pygame.image.load("plat6.png"))
     platformimages.append(pygame.image.load("plat7.png"))
     platformimages.append(pygame.image.load("plat8.png"))
     return platformimages

class eggClass(pygame.sprite.Sprite):
     def __init__(self,eggimages,x,y, xspeed, yspeed):
          pygame.sprite.Sprite.__init__(self) #call Sprite initializer
          self.images = eggimages
          self.image = self.images[0]
          self.rect = self.image.get_rect()
          self.x = x
          self.y = y
          self.xspeed = xspeed
          self.yspeed = yspeed
          self.rect.topleft = (x,y)
          self.right = self.rect.right
          self.top = self.rect.top
          self.next_update_time = 0
          
     def move(self):
          #gravity
          self.yspeed += GRAVITY
          if self.yspeed > 10:
               self.yspeed = 10
          self.y += self.yspeed
          self.x += self.xspeed
          if self.y > 570: #hit lava
               self.kill()          
     
     def update(self, current_time,platforms):
          # Update every 30 milliseconds
          if self.next_update_time < current_time:
               self.next_update_time = current_time + 30          
               self.move()
               self.rect.topleft = (self.x,self.y)
               collidedPlatforms = pygame.sprite.spritecollide(self,platforms,False,collided=pygame.sprite.collide_mask)
               if (((self.y >40 and self.y < 45) or (self.y >250 and self.y < 255)) and (self.x < 0 or self.x > 860)):  #catch when it is rolling between screens
                    self.yspeed = 0
               else:
                    collided=False
                    for collidedPlatform in collidedPlatforms:   
                         collided = self.bounce(collidedPlatform)
               #wrap round screens
               if self.x < -48:
                    self.x = 900
               if self.x >900:
                    self.x = -48               




     def bounce(self,collidedThing):
          collided=False
          if self.y < (collidedThing.y-20) and ((self.x > (collidedThing.x - 40) and self.x < (collidedThing.rect.right-10))):
               #coming in from the top?
               self.walking = True
               self.yspeed = 0
               self.y = collidedThing.y - self.rect.height +1
          elif self.x < collidedThing.x:
               #colliding from left side
               collided = True
               self.x = self.x -10
               self.xspeed = -2
          elif self.x > collidedThing.rect.right-50:
               #colliding from right side
               collided = True
               self.x = self.x +10
               self.xspeed = 2
          elif self.y > collidedThing.y:
               #colliding from bottom
               collided = True
               self.y = self.y + 10
               self.yspeed = 0     
          return collided
     
class platformClass(pygame.sprite.Sprite):
     def __init__(self,image,x,y):
          pygame.sprite.Sprite.__init__(self) #call Sprite initializer
          self.image = image
          self.rect = self.image.get_rect()
          self.x = x
          self.y = y
          self.rect.topleft = (x,y)
          self.right = self.rect.right
          self.top = self.rect.top


class enemyClass(pygame.sprite.Sprite):
     def __init__(self,enemyimages, spawnimages, unmountedimages, startPos,enemyType):
          pygame.sprite.Sprite.__init__(self) #call Sprite initializer
          self.images = enemyimages
          self.spawnimages=spawnimages
          self.unmountedimages = unmountedimages
          self.frameNum = 0
          self.enemyType = enemyType
          self.image = self.spawnimages[0]
          self.rect = self.image.get_rect()
          self.next_update_time = 0
          self.next_anim_time = 0
          self.x = startPos[0]
          self.y = startPos[1]
          self.flap=0
          self.facingRight = True
          self.xspeed = random.randint(3,10)
          self.targetXSpeed = 10
          self.yspeed = 0
          self.walking = True
          self.flapCount = 0
          self.spawning=True
          self.alive=True
         
     def killed(self, eggList, eggimages):
          #make an egg appear here
          eggList.add(eggClass(eggimages, self.x, self.y, self.xspeed, self.yspeed))
          self.alive = False
          
     def update(self, current_time,keys,platforms,god):
          if self.next_update_time<current_time:  # only update every 30 millis
                    self.next_update_time = current_time+50
                    if self.spawning:
                         self.frameNum +=1
                         self.image = self.spawnimages[self.frameNum]
                         self.next_update_time += 100
                         self.rect.topleft = (self.x,self.y)
                         if self.frameNum==5:
                              self.spawning=False
                    else:
                         #see if we need to accelerate
                         if abs(self.xspeed) < self.targetXSpeed:
                              self.xspeed += self.xspeed/abs(self.xspeed)/2
                         #work out if flapping...
                         if self.flap<1 :
                              if (random.randint(0,10)>8 or self.y > 450): # flap to avoid lava
                                   self.yspeed -=3
                                   self.flap = 3
                         else:
                              self.flap -=1

                         self.x = self.x + self.xspeed
                         self.y = self.y + self.yspeed
                         if not self.walking:
                                   self.yspeed += GRAVITY
                         if self.yspeed > 10:        
                                   self.yspeed = 10  
                         if self.yspeed < -10:       
                                   self.yspeed = -10
                         if self.y < 0: # can't go off the top
                              self.y=0
                              self.yspeed = 2
                         if self.y > 570: #hit lava
                              self.kill()
                              
                         if self.x < -48:    #off the left. If enemy is dead then remove entirely
                              if self.alive:
                                   self.x = 900
                              else:
                                   self.kill()
                         if self.x >900:     #off the right. If enemy is dead then remove entirely
                              if self.alive:
                                   self.x = -48
                              else:
                                   self.kill()
                         self.rect.topleft = (self.x,self.y)
                         #check for platform collision
                         collidedPlatforms = pygame.sprite.spritecollide(self,platforms,False,collided=pygame.sprite.collide_mask)
                         self.walking = False
                         if (((self.y >40 and self.y < 45) or (self.y >220 and self.y < 225)) and (self.x < 0 or self.x > 860)):  #catch when it is walking between screens
                              self.walking = True
                              self.yspeed = 0
                         else:
                              for collidedPlatform in collidedPlatforms:
                                   self.bounce(collidedPlatform)
                         self.rect.topleft = (self.x,self.y)
                         if self.walking:
                              if self.next_anim_time < current_time:
                                   if self.xspeed != 0:
                                             self.next_anim_time = current_time + 100/abs(self.xspeed)
                                             self.frameNum +=1
                                             if self.frameNum > 3:
                                                  self.frameNum = 0
                                             else:
                                                  self.frameNum = 3
                         else:
                              if self.flap>0:
                                   self.frameNum = 6
                              else:
                                   self.frameNum = 5
                         if self.alive:
                              self.image = self.images[((self.enemyType*7)+self.frameNum)]
                         else:
                              #show the unmounted sprite
                              self.image = self.unmountedimages[self.frameNum]
                         if self.xspeed <0 or (self.xspeed == 0 and self.facingRight == False):
                              self.image = pygame.transform.flip(self.image, True, False)
                              self.facingRight = False
                         else:
                              self.facingRight = True


     def bounce(self,collidedThing):
          collided=False
          if self.y < (collidedThing.y-20) and ((self.x > (collidedThing.x - 40) and self.x < (collidedThing.rect.right-10))):
               #coming in from the top?
               self.walking = True
               self.yspeed = 0
               self.y = collidedThing.y - self.rect.height+3
          elif self.x < collidedThing.x:
               #colliding from left side
               collided = True
               self.x = self.x -10
               self.xspeed = -2
          elif self.x > collidedThing.rect.right-50:
               #colliding from right side
               collided = True
               self.x = self.x +10
               self.xspeed = 2
          elif self.y > collidedThing.y:
               #colliding from bottom
               collided = True
               self.y = self.y + 10
               self.yspeed = 0     
          return collided
     
class playerClass(pygame.sprite.Sprite):
     def __init__(self,birdimages,spawnimages, playerUnmountedimages):
          pygame.sprite.Sprite.__init__(self) #call Sprite initializer
          self.images = birdimages
          self.unmountedimages = playerUnmountedimages
          self.spawnimages = spawnimages
          self.frameNum = 2
          self.image = self.images[self.frameNum]
          self.rect = self.image.get_rect()
          self.next_update_time = 0
          self.next_anim_time = 0
          self.x = 415
          self.y = 350
          self.facingRight = True
          self.xspeed = 0
          self.yspeed = 0
          self.targetXSpeed = 10
          self.flap = False
          self.walking = True
          self.playerChannel= pygame.mixer.Channel(0)
          self.flapsound = pygame.mixer.Sound("joustflaedit.wav")
          self.skidsound = pygame.mixer.Sound("joustski.wav")
          self.bumpsound = pygame.mixer.Sound("joustthu.wav")
          self.lives = 4
          self.spawning=True
          self.alive=2



     def update(self, current_time,keys,platforms,enemies,god, eggList, eggimages):
          # Update every 30 milliseconds

          if self.next_update_time < current_time:
               self.next_update_time = current_time + 30
               if self.alive ==2:
                    if self.spawning:
                         self.frameNum +=1
                         self.image = self.spawnimages[self.frameNum]
                         self.next_update_time += 100
                         self.rect.topleft = (self.x,self.y)
                         if self.frameNum==5:
                              self.frameNum=4
                              self.spawning=False
                    else:
                         if keys[pygame.K_LEFT]:
                              if self.xspeed >-10:
                                   self.xspeed -=0.7
                         elif keys[pygame.K_RIGHT]:
                              if self.xspeed <10:
                                   self.xspeed +=0.7
                         if keys[pygame.K_SPACE]:
                              if self.flap == False:
                                   self.playerChannel.stop()
                                   self.flapsound.play(0)
                                   if self.yspeed > -250:
                                        self.yspeed -=3
                                   self.flap = True
                         else:
                              self.flap = False
                         self.x = self.x + self.xspeed
                         self.y = self.y + self.yspeed
                         if not self.walking:
                              self.yspeed += GRAVITY
                         if self.yspeed > 10:
                              self.yspeed = 10
                         if self.yspeed < -10:
                              self.yspeed = -10
                         if self.y < 0:
                              self.y = 0
                              self.yspeed=2
                         if self.y > 570:
                              self.die()
                         if self.x < -48:
                              self.x = 900
                         if self.x >900:
                              self.x = -48
                         self.rect.topleft = (self.x,self.y)
                         #check for enemy collision
                         collidedBirds = pygame.sprite.spritecollide(self,enemies,False,collided=pygame.sprite.collide_mask)
                         for bird in collidedBirds:
                              #check each bird to see if above or below
                              if bird.y > self.y and bird.alive:
                                   self.bounce(bird)
                                   bird.killed(eggList, eggimages)
                                   bird.bounce(self)
                              elif bird.y < self.y-5 and bird.alive and not god.on:
                                   self.bounce(bird)
                                   bird.bounce(self)
                                   self.die()
                                   
                                   break
                              elif bird.alive:
                                   self.bounce(bird)
                                   bird.bounce(self)
                         #check for platform collision
                         collidedPlatforms = pygame.sprite.spritecollide(self,platforms,False,collided=pygame.sprite.collide_mask)
                         self.walking = False
                         if (((self.y >40 and self.y < 45) or (self.y >250 and self.y < 255)) and (self.x < 0 or self.x > 860)):  #catch when it is walking between screens
                              self.walking = True
                              self.yspeed = 0
                         else:
                              collided=False
                              for collidedPlatform in collidedPlatforms:   
                                   collided = self.bounce(collidedPlatform)
                              if collided:
                                   #play a bump sound
                                   self.playerChannel.play(self.bumpsound)
                         self.rect.topleft = (self.x,self.y)
                         if self.walking:
                              #if walking
                              if self.next_anim_time < current_time:
                                   if self.xspeed != 0:
                                        if (self.xspeed>5 and keys[pygame.K_LEFT]) or (self.xspeed<-5 and keys[pygame.K_RIGHT]):
          
                                             if  self.frameNum != 4:
                                                  self.playerChannel.play(self.skidsound)
                                             self.frameNum=4
                                        else:
                                             self.next_anim_time = current_time + 200/abs(self.xspeed)
                                             self.frameNum +=1
                                             if self.frameNum > 3:
                                                  self.frameNum = 0
                                   elif self.frameNum == 4:
                                        self.frameNum = 3
                                        self.playerChannel.stop()
          
                              self.image = self.images[self.frameNum]    
                         else:
                              if self.flap:
                                   self.image = self.images[6]
               
                              else:
                                   self.image = self.images[5]
                         if self.xspeed <0 or (self.xspeed == 0 and self.facingRight == False):
                              self.image = pygame.transform.flip(self.image, True, False)
                              self.facingRight = False
                         else:
                              self.facingRight = True
               elif self.alive == 1:
                    #unmounted player, lone bird
                    #see if we need to accelerate
                    if abs(self.xspeed) < self.targetXSpeed:
                         if abs(self.xspeed) > 0:
                              self.xspeed += self.xspeed/abs(self.xspeed)/2
                         else:
                              self.xspeed += 0.5
                    #work out if flapping...
                    if self.flap<1 :
                         if (random.randint(0,10)>8 or self.y > 450): # flap to avoid lava
                              self.yspeed -=3
                              self.flap = 3
                    else:
                         self.flap -=1
     
                    self.x = self.x + self.xspeed
                    self.y = self.y + self.yspeed
                    if not self.walking:
                              self.yspeed += 0.4
                    if self.yspeed > 10:        
                              self.yspeed = 10  
                    if self.yspeed < -10:       
                              self.yspeed = -10
                    if self.y < 0: # can't go off the top
                         self.y=0
                         self.yspeed = 2
                    
                    if self.x < -48:    #off the left. remove entirely
                         self.image = self.images[7]
                         self.alive=0
                         self.next_update_time = current_time + 2000
                    if self.x >900:     #off the right. remove entirely
                         self.image = self.images[7]
                         self.alive=0
                         self.next_update_time = current_time + 2000
                    self.rect.topleft = (self.x,self.y)
                    #check for platform collision
                    collidedPlatforms = pygame.sprite.spritecollide(self,platforms,False,collided=pygame.sprite.collide_mask)
                    self.walking = False
                    if (((self.y >40 and self.y < 45) or (self.y >220 and self.y < 225)) and (self.x < 0 or self.x > 860)):  #catch when it is walking between screens
                         self.walking = True
                         self.yspeed = 0
                    else:
                         for collidedPlatform in collidedPlatforms:
                              self.bounce(collidedPlatform)
                    self.rect.topleft = (self.x,self.y)
                    if self.walking:
                         if self.next_anim_time < current_time:
                              if self.xspeed != 0:
                                        self.next_anim_time = current_time + 100/abs(self.xspeed)
                                        self.frameNum +=1
                                        if self.frameNum > 3:
                                             self.frameNum = 0
                                        else:
                                             self.frameNum = 3
                    else:
                         if self.flap>0:
                              self.frameNum = 6
                         else:
                              self.frameNum = 5
                    self.image = self.unmountedimages[self.frameNum]
                    if self.xspeed <0 or (self.xspeed == 0 and self.facingRight == False):
                         self.image = pygame.transform.flip(self.image, True, False)
                         self.facingRight = False
                    else:
                         self.facingRight = True
               else:
                    #player respawn
                    self.respawn()
                    

                    
     def bounce(self,collidedThing):
          collided=False
          if self.y < (collidedThing.y-20) and ((self.x > (collidedThing.x - 40) and self.x < (collidedThing.rect.right-10))):
               #coming in from the top?
               self.walking = True
               self.yspeed = 0
               self.y = collidedThing.y - self.rect.height +1
          elif self.x < collidedThing.x:
               #colliding from left side
               collided = True
               self.x = self.x -10
               self.xspeed = -2
          elif self.x > collidedThing.rect.right-50:
               #colliding from right side
               collided = True
               self.x = self.x +10
               self.xspeed = 2
          elif self.y > collidedThing.y:
               #colliding from bottom
               collided = True
               self.y = self.y + 10
               self.yspeed = 0     
          return collided

     def die(self):
          self.lives -=1
          self.alive = 1
          
     def respawn(self):
          self.frameNum = 1
          self.image = self.images[self.frameNum]
          self.rect = self.image.get_rect()
          self.x = 415
          self.y = 350
          self.facingRight = True
          self.xspeed = 0
          self.yspeed = 0
          self.flap = False
          self.walking = True
          self.spawning=True
          self.alive=2          

          
class godmode(pygame.sprite.Sprite):
     def __init__(self):
          pygame.sprite.Sprite.__init__(self) #call Sprite initializer
          self.pic = pygame.image.load("god.png")
          self.image = self.pic
          self.on = False
          self.rect = self.image.get_rect()
          self.rect.topleft = (850,0)
          self.timer = pygame.time.get_ticks()
          
     def toggle(self,current_time):
          if current_time>self.timer:
               self.on = not self.on
               self.timer = current_time+1000
          
class pointsMarker(pygame.sprite.Sprite):
     pass

def generateEnemies(enemyimages, spawnimages, unmountedimages, enemyList,spawnPoints, enemiesToSpawn):
     #makes 2 enemies at a time, at 2 random spawn points
     for count in range(2):
          enemyList.add(enemyClass(enemyimages, spawnimages, unmountedimages, spawnPoints[random.randint(0,3)],0)) #last 0 is enemytype
          enemiesToSpawn -=1
          
     return enemyList, enemiesToSpawn

def drawLava(screen):
     lavaRect = [0,600,900,50]
     pygame.draw.rect(screen, (255,0,0), lavaRect)
     return lavaRect

def drawLava2(screen):
     lavaRect = [0,620,900,30]
     pygame.draw.rect(screen, (255,0,0), lavaRect)
     return lavaRect


def drawLives(lives, screen, lifeimage):
     startx = 375
     for num in range(lives):
          x = startx + num*20
          screen.blit(lifeimage, [x,570])

def drawScore(score, screen, digits):
     screen.blit(digits[score%10],[353,570])
     screen.blit(digits[(score%100)//10],[335,570])
     screen.blit(digits[(score%1000)//100],[317,570])
     screen.blit(digits[(score%10000)//1000],[299,570])
     screen.blit(digits[(score%100000)//10000],[281,570])
     screen.blit(digits[(score%1000000)//100000],[263,570])
def main():
     window = pygame.display.set_mode((900, 650))
     pygame.display.set_caption('Joust')
     screen = pygame.display.get_surface()
     clearSurface = screen.copy()
     player =  pygame.sprite.RenderUpdates()
     enemyList =  pygame.sprite.RenderUpdates()
     eggList = pygame.sprite.RenderUpdates()
     platforms =  pygame.sprite.RenderUpdates()
     godSprite = pygame.sprite.RenderUpdates()
     birdimages = load_sliced_sprites(60,60,"playerMounted.png")
     enemyimages = load_sliced_sprites(60,58,"enemies2.png")
     spawnimages = load_sliced_sprites(60,60,"spawn1.png")
     unmountedimages = load_sliced_sprites(60,60,"unmounted.png")
     playerUnmountedimages = load_sliced_sprites(60,60,"playerUnmounted.png")
     eggimages = load_sliced_sprites(40,33,"egg.png")
     lifeimage = pygame.image.load("life.png")
     lifeimage = lifeimage.convert_alpha()
     digits = load_sliced_sprites(21,21,"digits.png")
     platformImages = loadPlatforms()
     playerbird = playerClass(birdimages,spawnimages, playerUnmountedimages)
     god = godmode()
     godSprite.add(godmode())
     spawnPoints = [[690,248],[420,500], [420,80],[50,255]]
     plat1 = platformClass(platformImages[0],200,550)  #we create each platform by sending it the relevant platform image, the x position of the platform and the y position
     plat2 = platformClass(platformImages[1],350,395)
     plat3 = platformClass(platformImages[2],350,130)
     plat4 = platformClass(platformImages[3],0,100)
     plat5 = platformClass(platformImages[4],759,100)
     plat6 = platformClass(platformImages[5],0,310)
     plat7 = platformClass(platformImages[6],759,310)
     plat8 = platformClass(platformImages[7],600,290)
     player.add(playerbird)
     platforms.add(plat1,plat2,plat3,plat4,plat5,plat6,plat7,plat8)
     pygame.display.update()
     nextSpawnTime = pygame.time.get_ticks() + 2000
     enemiesToSpawn = 6 # test. make 6 enemies to start
     score=0
     running = True
     while running:
          current_time = pygame.time.get_ticks()
          #make enemies
          if current_time>nextSpawnTime and enemiesToSpawn>0:
               enemyList, enemiesToSpawn = generateEnemies(enemyimages,spawnimages, unmountedimages, enemyList,spawnPoints,enemiesToSpawn)
               nextSpawnTime = current_time+5000
          keys = pygame.key.get_pressed()
          pygame.event.clear()
          #If they have pressed Escape, close down Pygame
          if keys[pygame.K_ESCAPE]:
               running=False
          #check for God mode toggle
          if keys[pygame.K_g]:
               god.toggle(current_time)
          player.update(current_time,keys,platforms,enemyList,god,eggList, eggimages)
          platforms.update()
          enemyList.update(current_time,keys,platforms,god)
          eggList.update(current_time, platforms)
          enemiesRects = enemyList.draw(screen)
          if god.on:
               godrect = godSprite.draw(screen)
          else:
               godrect = pygame.Rect(850,0,50,50)
          playerRect = player.draw(screen)
          eggRects = eggList.draw(screen)
          lavaRect = drawLava(screen)
          platRects = platforms.draw(screen)
          lavarect2 = drawLava2(screen)
          drawLives(playerbird.lives,screen,lifeimage)
          drawScore(score,screen, digits)
          pygame.display.update(playerRect)
          pygame.display.update(lavaRect)
          pygame.display.update(lavarect2)                      
          pygame.display.update(platRects)
          pygame.display.update(enemiesRects)
          pygame.display.update(eggRects)
          pygame.display.update(godrect)
          player.clear(screen,clearSurface)
          enemyList.clear(screen,clearSurface)
          eggList.clear(screen,clearSurface)
          godSprite.clear(screen,clearSurface)
main()
pygame.quit()
