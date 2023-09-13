import pygame , random

pygame.init()
#use 2d vectors
vector = pygame.math.Vector2

#set surface (tile size = 32x32)
WINDOW_WIDTH = 1280  #1280/ 32 = 40 TILES WIDE
WINDOW_HEIGHT = 736 # 736/ 32 = 23 TILES HIGH

screen = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))
pygame.display.set_caption("Zombie Knight")

#fps and clock
FPS = 60
clock = pygame.time.Clock()

#defining classes
class Game():
    """A class to help manage game play"""
    def __init__(self, player,zombie_grp,platform_grp,portal_grp,bullet_grp,ruby_grp):
        self.ST_RND_TYM= 25
        self.ST_ZOMBIE_CREATION_TYM = 5

        self.score = 0
        self.round_no = 1
        self.frame_cnt = 0
        self.round_tym = self.ST_RND_TYM

        self.title_font = pygame.font.Font("assets/fonts/Poultrygeist.ttf",48)
        self.hud_font = pygame.font.Font("assets/fonts/Pixel.ttf",24)

        self.lost_ruby_snd = pygame.mixer.Sound("assets/sounds/lost_ruby.wav")
        self.ruby_pickup_snd = pygame.mixer.Sound("assets/sounds/ruby_pickup.wav")
        pygame.mixer.music.load("assets/sounds/level_music.wav")



        self.player = player
        self.zombie_grp = zombie_grp
        self.platform_grp = platform_grp
        self.portal_grp = portal_grp
        self.bullet_grp = bullet_grp
        self.ruby_grp = ruby_grp
        self.zombie_creation_tym = self.ST_ZOMBIE_CREATION_TYM

    def update(self):
        self.frame_cnt += 1
        if self.frame_cnt%FPS == 0:
            self.round_tym -=1
            self.frame_cnt = 0
        self.check_collision()
        self.check_round_completion()
        self.add_zombies()
        self.check_game_ovr()
    def draw(self):

        WHITE = (255,255,255)
        GREEN = (25,200,25)

        score_txt = self.hud_font.render("Score: "+ str(self.score),True,WHITE)
        score_rect = score_txt.get_rect(topleft = (10,WINDOW_HEIGHT-50))

        health_txt = self.hud_font.render("Health: "+ str(self.player.health),True,WHITE)
        health_rect = health_txt.get_rect(topleft = (10,WINDOW_HEIGHT-25))

        title_txt = self.title_font.render("Zombie Knight",True,GREEN)
        title_rect = title_txt.get_rect(center = (WINDOW_WIDTH//2,WINDOW_HEIGHT-25))

        round_txt = self.hud_font.render("Round Nights: " + str(self.round_no),True,WHITE)
        round_rect = round_txt.get_rect(topright = (WINDOW_WIDTH-10,WINDOW_HEIGHT-50))

        tym_txt = self.hud_font.render("Sunrise In: " + str(self.round_tym),True,WHITE)
        tym_rect = tym_txt.get_rect(topright = (WINDOW_WIDTH-10,WINDOW_HEIGHT-25))

        screen.blit(score_txt,score_rect)
        screen.blit(health_txt,health_rect)
        screen.blit(title_txt,title_rect)
        screen.blit(round_txt,round_rect)
        screen.blit(tym_txt,tym_rect)
    def add_zombies(self):
        if self.frame_cnt%FPS == 0:
            if self.round_tym%self.zombie_creation_tym == 0:
                zombie = Zombie(self.platform_grp,self.portal_grp,self.round_no,5+self.round_no)
                self.zombie_grp.add(zombie)
    def check_collision(self):
        collision_dict = pygame.sprite.groupcollide(self.bullet_grp,self.zombie_grp,True,False)
        if collision_dict:
            for zombies in collision_dict.values():
                for  zombie in zombies:
                    zombie.hit_snd.play()
                    zombie.isdead = True
                    zombie.animate_death = True

        collision_list = pygame.sprite.spritecollide(self.player,self.zombie_grp,False)
        if collision_list:
            for zombie in collision_list:
                if zombie.isdead:
                    zombie.kick_snd.play()
                    zombie.kill()
                    self.score += 25

                    ruby = Ruby(self.platform_grp,self.portal_grp)
                    self.ruby_grp.add(ruby)
                else:
                    self.player.health -= 20
                    self.player.hit_snd.play() 
                    self.player.position.x -= 256*zombie.direction
                    self.player.rect.bottomleft = self.player.position
        
        if pygame.sprite.spritecollide(self.player,self.ruby_grp,True):
            self.ruby_pickup_snd.play()
            self.score += 100
            self.player.health += 10
            if self.player.health>self.player.ST_HEALTH:
                self.player.health = self.player.ST_HEALTH
        for zombie in self.zombie_grp:
            if not zombie.isdead:
                if pygame.sprite.spritecollide(zombie,self.ruby_grp,True):
                    self.lost_ruby_snd.play()
                    zombie = Zombie(self.platform_grp,self.portal_grp,self.round_no,5+self.round_no )
                    self.zombie_grp.add(zombie)
    def check_round_completion(self):
        if self.round_tym == 0:
            self.start_new_round()
    def check_game_ovr(self):
        if self.player.health<=0:
            pygame.mixer.music.stop()
            self.pause_game("Game over! Final Score: "+ str(self.score),"Press 'Enter' to Play again!")
            self.reset_game()
    def start_new_round(self):
        self.round_no += 1
        if self.round_no <self.ST_ZOMBIE_CREATION_TYM:
            self.zombie_creation_tym -= 1
        self.round_tym = self.ST_RND_TYM
        self.zombie_grp.empty()
        self.ruby_grp.empty()
        self.bullet_grp.empty()

        self.player.reset()

        self.pause_game("You survived the night","Press Enter to continue")
    def pause_game(self,main_txt,sub_txt):

        global running

        pygame.mixer.music.pause()

        WHITE = (255,255,255)
        BLACK= (0,0,0)
        GREEN = (25,200,25)

        main_txt = self.title_font.render(main_txt,True,GREEN)
        main_rect = main_txt.get_rect(center = (WINDOW_WIDTH//2,WINDOW_HEIGHT//2))

        sub_txt = self.title_font.render(sub_txt,True,WHITE)
        sub_rect = main_txt.get_rect(center = (WINDOW_WIDTH//2,WINDOW_HEIGHT//2+64))

        screen.fill(BLACK)
        screen.blit(main_txt,main_rect)
        screen.blit(sub_txt,sub_rect)
        pygame.display.update()

        ispaused = True
        while ispaused:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        ispaused = False
                        pygame.mixer.music.unpause()
                if event.type == pygame.QUIT:
                    ispaused = False
                    running = False
                    pygame.mixer.music.stop()

    def reset_game(self):
        self.score = 0
        self.round_no = 1
        self.round_tym = self.ST_RND_TYM
        self.zombie_creation_tym = self.ST_ZOMBIE_CREATION_TYM

        self.player.health = self.player.ST_HEALTH
        self.player.reset()

        self.zombie_grp.empty()
        self.ruby_grp.empty()
        self.bullet_grp.empty()

        pygame.mixer.music.play(-1, 0.0)

class Tile(pygame.sprite.Sprite):
    """A class to represent 32x32 area in our display"""
    def __init__(self,x,y,img_int,main_tile,sub_tile = ""):
        pygame.sprite.Sprite.__init__(self)
        if img_int == 1: #diit
            self.image = pygame.transform.scale(pygame.image.load("assets/images/tiles/TIle (1).png"),(32,32))
        elif img_int == 2: #platform
            self.image = pygame.transform.scale(pygame.image.load("assets/images/tiles/TIle (2).png"),(32,32))
            sub_tile.add(self)
        elif img_int == 3: #platform
            self.image = pygame.transform.scale(pygame.image.load("assets/images/tiles/TIle (3).png"),(32,32))
            sub_tile.add(self)
        elif img_int == 4: #platform
            self.image = pygame.transform.scale(pygame.image.load("assets/images/tiles/TIle (4).png"),(32,32))
            sub_tile.add(self)
        elif img_int == 5: #platform
            self.image = pygame.transform.scale(pygame.image.load("assets/images/tiles/TIle (5).png"),(32,32))
            sub_tile.add(self)
        #add everytile to main grp
        main_tile.add(self)

        self.rect = self.image.get_rect(topleft = (x,y))
        self.mask = pygame.mask.from_surface(self.image)

class Player(pygame.sprite.Sprite):
    """A class user can control"""
    def __init__(self,x,y,platform_grp,portal_grp,bullet_grp):
        pygame.sprite.Sprite.__init__(self)
        self.HOR_ACCELERATION = 2
        self.HOR_FRICTION = 0.15
        self.VER_ACCELERATION = 0.8
        self.VER_JUMP_SPEED = 18
        self.ST_HEALTH = 100

        #animation frames
        self.move_right_sprites = []
        self.move_left_sprites = []
        self.idle_right_sprites = []
        self.idle_left_sprites = []
        self.jump_right_sprites = []
        self.jump_left_sprites = []
        self.attack_right_sprites = []
        self.attack_left_sprites = []

        #moving
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/run/Run (1).png") , (64,64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/run/Run (2).png") , (64,64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/run/Run (3).png") , (64,64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/run/Run (4).png") , (64,64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/run/Run (5).png") , (64,64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/run/Run (6).png") , (64,64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/run/Run (7).png") , (64,64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/run/Run (8).png") , (64,64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/run/Run (9).png") , (64,64)))
        self.move_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/run/Run (10).png") , (64,64)))

        for sprite in self.move_right_sprites:
            self.move_left_sprites.append(pygame.transform.flip(sprite,True,False))

        #idle
        self.idle_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/idle/Idle (1).png") , (64,64)))
        self.idle_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/idle/Idle (2).png") , (64,64)))
        self.idle_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/idle/Idle (3).png") , (64,64)))
        self.idle_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/idle/Idle (4).png") , (64,64)))
        self.idle_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/idle/Idle (5).png") , (64,64)))
        self.idle_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/idle/Idle (6).png") , (64,64)))
        self.idle_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/idle/Idle (7).png") , (64,64)))
        self.idle_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/idle/Idle (8).png") , (64,64)))
        self.idle_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/idle/Idle (9).png") , (64,64)))
        self.idle_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/idle/Idle (10).png") , (64,64)))

        for sprite in self.idle_right_sprites:
            self.idle_left_sprites.append(pygame.transform.flip(sprite,True,False))
        
        #jump
        self.jump_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/jump/Jump (1).png") , (64,64)))
        self.jump_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/jump/Jump (2).png") , (64,64)))
        self.jump_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/jump/Jump (3).png") , (64,64)))
        self.jump_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/jump/Jump (4).png") , (64,64)))
        self.jump_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/jump/Jump (5).png") , (64,64)))
        self.jump_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/jump/Jump (6).png") , (64,64)))
        self.jump_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/jump/Jump (7).png") , (64,64)))
        self.jump_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/jump/Jump (8).png") , (64,64)))
        self.jump_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/jump/Jump (9).png") , (64,64)))
        self.jump_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/jump/Jump (10).png") , (64,64)))

        for sprite in self.jump_right_sprites:
            self.jump_left_sprites.append(pygame.transform.flip(sprite,True,False))

        #Attack
        self.attack_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/attack/Attack (1).png") , (64,64)))
        self.attack_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/attack/Attack (2).png") , (64,64)))
        self.attack_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/attack/Attack (3).png") , (64,64)))
        self.attack_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/attack/Attack (4).png") , (64,64)))
        self.attack_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/attack/Attack (5).png") , (64,64)))
        self.attack_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/attack/Attack (6).png") , (64,64)))
        self.attack_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/attack/Attack (7).png") , (64,64)))
        self.attack_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/attack/Attack (8).png") , (64,64)))
        self.attack_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/attack/Attack (9).png") , (64,64)))
        self.attack_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/player/attack/Attack (10).png") , (64,64)))

        for sprite in self.attack_right_sprites:
            self.attack_left_sprites.append(pygame.transform.flip(sprite,True,False))

        self.curr_sprite = 0
        self.image = self.idle_right_sprites[self.curr_sprite]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x,y)

        

        self.platform_grp = platform_grp
        self.portal_grp = portal_grp
        self.bullet_grp = bullet_grp

        self.animate_jump = False
        self.animate_fire = False

        self.jump_snd = pygame.mixer.Sound("assets/sounds/jump_sound.wav")
        self.slash_snd = pygame.mixer.Sound("assets/sounds/slash_sound.wav")
        self.portal_snd = pygame.mixer.Sound("assets/sounds/portal_sound.wav")
        self.hit_snd = pygame.mixer.Sound("assets/sounds/player_hit.wav")

        self.position = vector(x,y)
        self.velocity = vector(0,0)
        self.acceleration = (0,self.VER_ACCELERATION)

        self.health = self.ST_HEALTH
        self.strtx = x
        self.strty = y

    def update(self):
        self.move()
        self.check_collisions()
        self.check_animations()
        self.mask = pygame.mask.from_surface(self.image)

    def move(self):
        self.acceleration = vector(0,self.VER_ACCELERATION)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.acceleration.x = -1*self.HOR_ACCELERATION
            self.animate(self.move_left_sprites,0.5)
        elif keys[pygame.K_RIGHT]or keys[pygame.K_d]:
            self.acceleration.x = self.HOR_ACCELERATION
            self.animate(self.move_right_sprites,0.5)
        else:
            if self.velocity.x>0:
                self.animate(self.idle_right_sprites,.5)
            else:
                self.animate(self.idle_left_sprites,.5)
        self.acceleration.x -= self.velocity.x*self.HOR_FRICTION
        self.velocity += self.acceleration
        self.position += self.velocity+ 0.5*self.acceleration

        if self.position.x <0:
            self.position.x = WINDOW_WIDTH
        elif self.position.x>WINDOW_WIDTH:
            self.position.x = 0
        self.rect.bottomleft = self.position 
    def check_collisions(self):
        if self.velocity.y>0:
            collided_platforms = pygame.sprite.spritecollide(self,self.platform_grp,False,pygame.sprite.collide_mask)
            if collided_platforms:
                self.position.y = collided_platforms[0].rect.top + 5
                self.velocity.y = 0
        #jump
        if self.velocity.y<0:
            collided_platforms = pygame.sprite.spritecollide(self,self.platform_grp,False,pygame.sprite.collide_mask)
            if collided_platforms:
                self.velocity.y = 0
                while pygame.sprite.spritecollide(self,self.platform_grp,False):
                    self.position.y += 1
                    self.rect.bottomleft = self.position
        #portal
        if pygame.sprite.spritecollide(self,self.portal_grp,False):
            self.portal_snd.play()
            #left and right
            if self.position.x>WINDOW_WIDTH//2:
                self.position.x = 86
            else:
                self.position.x = WINDOW_WIDTH-150
            # top and bottom
            if self.position.y>WINDOW_HEIGHT//2:
                self.position.y = 64
            else:
                self.position.y = WINDOW_HEIGHT-132
            self.rect.bottomleft = self.position 
    def check_animations(self):
        if self.animate_jump:
            if self.velocity.x>0:
                self.animate(self.jump_right_sprites,0.1)
            else:
                self.animate(self.jump_left_sprites,0.1)
        
        if self.animate_fire:
            if self.velocity.x>0:
                self.animate(self.attack_right_sprites,0.25)
            else:
                self.animate(self.attack_left_sprites,0.25)
        

    def jump(self):
        #jump when on platfrom
        if pygame.sprite.spritecollide(self,self.platform_grp,False):
            self.jump_snd.play()
            self.velocity.y = -1* self.VER_JUMP_SPEED
            self.animate_jump = True

    def fire(self):
        self.slash_snd.play()
        Bullet(self.rect.centerx ,self.rect.centery,self.bullet_grp,self) 
        self.animate_fire = True

    def reset(self):
        self.position = vector(self.strtx,self.strty)
        self.rect.bottomleft = self.position
        self.velocity = vector(0,0)

    def animate(self,sprite_list,speed):
        if self.curr_sprite<len(sprite_list)-1:
            self.curr_sprite += speed
        else:
            self.curr_sprite = 0
            
            #end jump animation
            if self.animate_jump:
                self.animate_jump = False
            if self.animate_fire:
                self.animate_fire = False 
        self.image = sprite_list[int(self.curr_sprite)]

class Bullet(pygame.sprite.Sprite):
    """A projectile launched by the player"""
    def __init__(self,x,y,bullet_grp,player):
        pygame.sprite.Sprite.__init__(self)
        self.veclocity = 20
        self.range = 500    

        if player.velocity.x >0:
            self.image = pygame.transform.scale(pygame.image.load("assets/images/player/slash.png") ,(32,32))
        else:
            self.veclocity = -1*self.veclocity
            self.image = pygame.transform.scale(pygame.transform.flip(pygame.image.load("assets/images/player/slash.png"), True, False), (32,32))
        self.rect = self.image.get_rect(center = (x,y))
        self.strtx =x
        bullet_grp.add(self)
    def update(self):
        self.rect.x += self.veclocity

        if abs(self.rect.x-self.strtx) >self.range:
            self.kill()

class Zombie(pygame.sprite.Sprite):
    """An enemy class that moves around the screen"""
    def __init__(self,platform_grp,portal_grp,min_speed,max_speed):
        pygame.sprite.Sprite.__init__(self)
        self.VER_ACCELERATION = 3
        self.RISE_TIME =2

        #frames
        self.walk_right_sprites = []
        self.walk_left_sprites = []
        self.die_right_sprites = []
        self.die_left_sprites = []
        self.rise_right_sprites = []
        self.rise_left_sprites = []

        gender = random.randint(0,1)
        if gender == 0:
            self.walk_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/walk/Walk (1).png"),(64,64)))
            self.walk_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/walk/Walk (3).png"),(64,64)))
            self.walk_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/walk/Walk (2).png"),(64,64)))
            self.walk_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/walk/Walk (4).png"),(64,64)))
            self.walk_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/walk/Walk (5).png"),(64,64)))
            self.walk_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/walk/Walk (6).png"),(64,64)))
            self.walk_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/walk/Walk (7).png"),(64,64)))
            self.walk_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/walk/Walk (8).png"),(64,64)))
            self.walk_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/walk/Walk (9).png"),(64,64)))
            self.walk_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/walk/Walk (10).png"),(64,64)))

            for sprite in self.walk_right_sprites:
                self.walk_left_sprites.append(pygame.transform.flip(sprite,True,False))
            
            self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/dead/Dead (2).png"),(64,64)))
            self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/dead/Dead (1).png"),(64,64)))
            self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/dead/Dead (3).png"),(64,64)))
            self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/dead/Dead (4).png"),(64,64)))
            self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/dead/Dead (5).png"),(64,64)))
            self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/dead/Dead (6).png"),(64,64)))
            self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/dead/Dead (7).png"),(64,64)))
            self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/dead/Dead (8).png"),(64,64)))
            self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/dead/Dead (9).png"),(64,64)))
            self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/dead/Dead (10).png"),(64,64)))

            for sprite in self.die_right_sprites:
                self.die_left_sprites.append(pygame.transform.flip(sprite,True,False))
            
            self.rise_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/dead/Dead (10).png"),(64,64)))
            self.rise_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/dead/Dead (9).png"),(64,64)))
            self.rise_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/dead/Dead (8).png"),(64,64)))
            self.rise_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/dead/Dead (7).png"),(64,64)))
            self.rise_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/dead/Dead (6).png"),(64,64)))
            self.rise_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/dead/Dead (5).png"),(64,64)))
            self.rise_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/dead/Dead (4).png"),(64,64)))
            self.rise_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/dead/Dead (3).png"),(64,64)))
            self.rise_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/dead/Dead (2).png"),(64,64)))
            self.rise_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/boy/dead/Dead (1).png"),(64,64)))

            for sprite in self.rise_right_sprites:
                self.rise_left_sprites.append(pygame.transform.flip(sprite,True,False))
        else:
            self.walk_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/walk/Walk (1).png"),(64,64)))
            self.walk_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/walk/Walk (2).png"),(64,64)))
            self.walk_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/walk/Walk (3).png"),(64,64)))
            self.walk_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/walk/Walk (4).png"),(64,64)))
            self.walk_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/walk/Walk (5).png"),(64,64)))
            self.walk_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/walk/Walk (6).png"),(64,64)))
            self.walk_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/walk/Walk (7).png"),(64,64)))
            self.walk_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/walk/Walk (8).png"),(64,64)))
            self.walk_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/walk/Walk (9).png"),(64,64)))
            self.walk_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/walk/Walk (10).png"),(64,64)))

            for sprite in self.walk_right_sprites:
                self.walk_left_sprites.append(pygame.transform.flip(sprite,True,False))
            
            self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/dead/Dead (1).png"),(64,64)))
            self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/dead/Dead (2).png"),(64,64)))
            self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/dead/Dead (3).png"),(64,64)))
            self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/dead/Dead (4).png"),(64,64)))
            self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/dead/Dead (5).png"),(64,64)))
            self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/dead/Dead (6).png"),(64,64)))
            self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/dead/Dead (7).png"),(64,64)))
            self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/dead/Dead (8).png"),(64,64)))
            self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/dead/Dead (9).png"),(64,64)))
            self.die_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/dead/Dead (10).png"),(64,64)))

            for sprite in self.die_right_sprites:
                self.die_left_sprites.append(pygame.transform.flip(sprite,True,False))
            
            self.rise_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/dead/Dead (10).png"),(64,64)))
            self.rise_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/dead/Dead (9).png"),(64,64)))
            self.rise_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/dead/Dead (8).png"),(64,64)))
            self.rise_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/dead/Dead (7).png"),(64,64)))
            self.rise_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/dead/Dead (6).png"),(64,64)))
            self.rise_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/dead/Dead (5).png"),(64,64)))
            self.rise_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/dead/Dead (4).png"),(64,64)))
            self.rise_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/dead/Dead (3).png"),(64,64)))
            self.rise_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/dead/Dead (2).png"),(64,64)))
            self.rise_right_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/zombie/girl/dead/Dead (1).png"),(64,64)))

            for sprite in self.rise_right_sprites:
                self.rise_left_sprites.append(pygame.transform.flip(sprite,True,False))
        self.direction = random.choice([-1,1])
        self.current_sprite = 0
        if self.direction == -1:
            self.image = self.walk_left_sprites[self.current_sprite]
        else:
            self.image = self.walk_right_sprites[self.current_sprite]
        
        self.rect = self.image.get_rect(bottomleft = (random.randint(100,WINDOW_WIDTH-100) , -100))

        self.platform_grp = platform_grp
        self.portal_grp = portal_grp

        self.animate_death = False
        self.animate_rise = False

        self.hit_snd = pygame.mixer.Sound("assets/sounds/zombie_hit.wav")
        self.kick_snd = pygame.mixer.Sound("assets/sounds/zombie_kick.wav")
        self.portal_snd = pygame.mixer.Sound("assets/sounds/portal_sound.wav")

        self.position = vector(self.rect.x,self.rect.y)
        self.velocity = vector(self.direction*random.randint(min_speed,max_speed),0)
        self.acceleration = vector(0,self.VER_ACCELERATION)

        self.isdead = False
        self.round_tym = 0
        self.frame_cnt = 0 
            
    def update(self):
        self.move()
        self.check_collisions()
        self.check_animations()
        if self.isdead:
            self.frame_cnt += 1
            if self.frame_cnt%FPS == 0:
                self.round_tym += 1
                if self.round_tym == self.RISE_TIME:
                    self.animate_rise = True
                    self.current_sprite = 0
    def move(self):
        if not self.isdead:
            if self.direction == -1:
                self.animate(self.walk_left_sprites,0.5)
            else:
                self.animate(self.walk_right_sprites,0.5)
            #acceleration will be constant
            self.velocity += self.acceleration
            self.position += self.velocity+ 0.5*self.acceleration

            if self.position.x <0:
                self.position.x = WINDOW_WIDTH
            elif self.position.x>WINDOW_WIDTH:
                self.position.x = 0
            self.rect.bottomleft = self.position 

    def check_collisions(self):
        collided_platforms = pygame.sprite.spritecollide(self,self.platform_grp,False)
        if collided_platforms:
            self.position.y = collided_platforms[0].rect.top + 1
            self.velocity.y = 0
        #portal
        if pygame.sprite.spritecollide(self,self.portal_grp,False):
            self.portal_snd.play()
            #left and right
            if self.position.x>WINDOW_WIDTH//2:
                self.position.x = 86
            else:
                self.position.x = WINDOW_WIDTH-150
            # top and bottom
            if self.position.y>WINDOW_HEIGHT//2:
                self.position.y = 64
            else:
                self.position.y = WINDOW_HEIGHT-132
            self.rect.bottomleft = self.position 
    def check_animations(self):
        if self.animate_death:
            if self.direction == 1:
                self.animate(self.die_right_sprites,0.95)
            else:
                self.animate(self.die_left_sprites,0.95) 
        if self.animate_rise:
            if self.direction == 1:
                self.animate(self.rise_right_sprites,.095)
            else:
                self.animate(self.rise_left_sprites,0.95)
    def animate(self,sprite_list,speed):
        if self.current_sprite<len(sprite_list)-1:
            self.current_sprite += speed
        else:
            self.current_sprite = 0
            
            if self.animate_death:
                self.current_sprite = len(sprite_list)-1
                self.animate_death = False
            if self.animate_rise:
                self.animate_rise = False
                self.isdead = False
                self.frame_cnt = 0
                self.round_tym = 0  
        self.image = sprite_list[int(self.current_sprite)]


class RubyMaker(pygame.sprite.Sprite):
    """A tile that is animated. A ruby will be generated here"""
    def __init__(self,x,y,main_tile):
        pygame.sprite.Sprite.__init__(self)

        #animation frames
        self.ruby_sprites = []

        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/ruby/Tile000.png"),(64,64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/ruby/Tile001.png"),(64,64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/ruby/Tile002.png"),(64,64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/ruby/Tile003.png"),(64,64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/ruby/Tile004.png"),(64,64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/ruby/Tile005.png"),(64,64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/ruby/Tile006.png"),(64,64)))

        self.curr_sprite = 0
        self.image = self.ruby_sprites[self.curr_sprite]
        self.rect = self.image.get_rect(bottomleft = (x,y))

        main_tile.add(self)
    def update(self):
        self.animate(self.ruby_sprites,0.25)

    def animate(self,sprite_list,speed):
        if self.curr_sprite<len(sprite_list)-1:
            self.curr_sprite += speed
        else:
            self.curr_sprite = 0
        self.image = sprite_list[int(self.curr_sprite)]
        
class Ruby(pygame.sprite.Sprite):
    """A class the player must collect to earn points and health"""

    def __init__(self, platform_group, portal_group):
        pygame.sprite.Sprite.__init__(self)

        self.VERTICAL_ACCELERATION = 3 #Gravity
        self.HORIZONTAL_VELOCITY = 5

        self.ruby_sprites = []
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/ruby/tile000.png"), (64,64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/ruby/tile001.png"), (64,64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/ruby/tile002.png"), (64,64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/ruby/tile003.png"), (64,64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/ruby/tile004.png"), (64,64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/ruby/tile005.png"), (64,64)))
        self.ruby_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/ruby/tile006.png"), (64,64)))

        self.current_sprite = 0
        self.image = self.ruby_sprites[self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (WINDOW_WIDTH//2, 100)

        self.platform_group = platform_group
        self.portal_group = portal_group

        self.portal_snd = pygame.mixer.Sound("assets/sounds/portal_sound.wav")

        self.position = vector(self.rect.x, self.rect.y)
        self.velocity = vector(random.choice([-1*self.HORIZONTAL_VELOCITY, self.HORIZONTAL_VELOCITY]), 0)
        self.acceleration = vector(0, self.VERTICAL_ACCELERATION)


    def update(self):
        self.animate(self.ruby_sprites, .25)
        self.move()
        self.check_collisions()


    def move(self):

        self.velocity += self.acceleration
        self.position += self.velocity + 0.5*self.acceleration

        if self.position.x < 0:
            self.position.x = WINDOW_WIDTH
        elif self.position.x > WINDOW_WIDTH:
            self.position.x = 0
        
        self.rect.bottomleft = self.position


    def check_collisions(self):

        collided_platforms = pygame.sprite.spritecollide(self, self.platform_group, False)
        if collided_platforms:
            self.position.y = collided_platforms[0].rect.top + 1
            self.velocity.y = 0

        if pygame.sprite.spritecollide(self, self.portal_group, False):
            self.portal_snd.play()
            #Left and right
            if self.position.x > WINDOW_WIDTH//2:
                self.position.x = 86
            else:
                self.position.x = WINDOW_WIDTH - 150
            #Top and bottom
            if self.position.y > WINDOW_HEIGHT//2:
                self.position.y = 64
            else:
                self.position.y = WINDOW_HEIGHT - 132

            self.rect.bottomleft = self.position


    def animate(self, sprite_list, speed):
        if self.current_sprite < len(sprite_list) -1:
            self.current_sprite += speed
        else:
            self.current_sprite = 0

        self.image = sprite_list[int(self.current_sprite)]



class Portal(pygame.sprite.Sprite):
    """A class that if collided with will transport you"""
    def __init__(self,x,y,color,portal_grp):
        pygame.sprite.Sprite.__init__(self)
        self.portal_sprites = []

        if color == "green":
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/green/tile000.png"),(72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/green/tile001.png"),(72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/green/tile002.png"),(72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/green/tile003.png"),(72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/green/tile004.png"),(72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/green/tile005.png"),(72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/green/tile006.png"),(72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/green/tile007.png"),(72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/green/tile008.png"),(72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/green/tile009.png"),(72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/green/tile010.png"),(72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/green/tile011.png"),(72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/green/tile012.png"),(72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/green/tile013.png"),(72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/green/tile014.png"),(72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/green/tile015.png"),(72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/green/tile016.png"),(72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/green/tile017.png"),(72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/green/tile018.png"),(72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/green/tile019.png"),(72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/green/tile020.png"),(72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/green/tile021.png"),(72,72)))
        else:
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/purple/tile000.png"),(72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/purple/tile001.png"),(72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/purple/tile002.png"),(72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/purple/tile003.png"),(72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/purple/tile004.png"),(72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/purple/tile005.png"),(72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/purple/tile006.png"),(72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/purple/tile007.png"),(72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/purple/tile008.png"),(72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/purple/tile009.png"),(72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/purple/tile010.png"),(72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/purple/tile011.png"),(72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/purple/tile012.png"),(72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/purple/tile013.png"),(72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/purple/tile014.png"),(72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/purple/tile015.png"),(72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/purple/tile016.png"),(72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/purple/tile017.png"),(72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/purple/tile018.png"),(72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/purple/tile019.png"),(72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/purple/tile020.png"),(72,72)))
            self.portal_sprites.append(pygame.transform.scale(pygame.image.load("assets/images/portals/purple/tile021.png"),(72,72)))


        self.current_sprite = random.randint(0,len(self.portal_sprites)-1)
        self.image = self.portal_sprites[self.current_sprite]
        self.rect = self.image.get_rect(bottomleft = (x,y))
        portal_grp.add(self)
    def update(self):
        self.animate(self.portal_sprites,0.2)
    def animate(self,sprite_list,speed):
        if self.current_sprite<len(sprite_list)-1:
            self.current_sprite += speed
        else:
            self.current_sprite = 0
        self.image = sprite_list[int(self.current_sprite)]
    
#create sprites
my_main_tile_grp = pygame.sprite.Group()
my_platform_grp = pygame.sprite.Group()
my_player_grp = pygame.sprite.Group()
my_bullet_grp = pygame.sprite.Group()
my_zombie_grp = pygame.sprite.Group()
my_portal_grp = pygame.sprite.Group()
my_ruby_grp = pygame.sprite.Group()

#tile map (23X40)
# 0=>no tile , 1=>dirt tile , 2-5 => platforms , 6 => ruby maker , 7-8=>portals , 9=>player

tile_map = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [7,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,8,0],
    [4,4,4,4,4,4,4,4,4,4,4,4,4,4,5,0,0,0,0,6,0,0,0,0,0,3,4,4,4,4,4,4,4,4,4,4,4,4,4,4],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,3,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,5,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [4,4,4,4,4,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,4,4,4,4,4],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,5,0,0,0,0,0,0,0,0,3,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,9,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,4,4,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [8,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,0],
    [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
]


#generate tile objects
for i in range(len(tile_map)):
    for j in range(len(tile_map[0])):
        if tile_map[i][j] == 1:
            Tile(32*j,32*i,1,my_main_tile_grp)
        elif tile_map[i][j] == 2:
            Tile(32*j,32*i,2,my_main_tile_grp,my_platform_grp)
        elif tile_map[i][j] == 3:
            Tile(32*j,32*i,3,my_main_tile_grp,my_platform_grp)
        elif tile_map[i][j] == 4:
            Tile(32*j,32*i,5,my_main_tile_grp,my_platform_grp)
        elif tile_map[i][j] == 5:
            Tile(32*j,32*i,5,my_main_tile_grp,my_platform_grp)
        elif tile_map[i][j] == 6:
            RubyMaker(32*j,32*i,my_main_tile_grp)
        elif tile_map[i][j] == 7:
            Portal(32*j,32*i,"green",my_portal_grp)
        elif tile_map[i][j] == 8:
            Portal(32*j,32*i,"purple",my_portal_grp)
        elif tile_map[i][j] == 9:
            print("x")
            my_player = Player(32*j-32,32*i+32,my_platform_grp,my_portal_grp,my_bullet_grp)
            my_player_grp.add(my_player)





#bg img
bg_img = pygame.transform.scale(pygame.image.load("assets/images/background.png"),(WINDOW_WIDTH,WINDOW_HEIGHT)) #resize bg img
bg_rect = bg_img.get_rect(topleft = (0,0))

my_game = Game(my_player,my_zombie_grp,my_platform_grp,my_portal_grp,my_bullet_grp,my_ruby_grp)
my_game.pause_game("Zombie Kight" , "Press 'Enter to begin")
pygame.mixer.music.play(-1,0.0)

running = True 
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                my_player.jump()
            if (event.key == pygame.K_UP) or (event.key == pygame.K_w):
                my_player.fire()
            
    

    screen.blit(bg_img,bg_rect)

    my_main_tile_grp.draw(screen) 
    my_main_tile_grp.update()

    my_portal_grp.update()
    my_portal_grp.draw(screen)

    my_player_grp.update()
    my_player_grp.draw(screen)

    my_bullet_grp.update()
    my_bullet_grp.draw(screen)

    my_zombie_grp.update()
    my_zombie_grp.draw(screen)

    my_ruby_grp.update()
    my_ruby_grp.draw(screen)

    my_game.update()
    my_game.draw()
    
    pygame.display.update()
    clock.tick(FPS)

pygame.quit()