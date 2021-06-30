import pygame
import os
import random
import math
import sys
import neat
import glob

pygame.init()

# Global Constants
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1100
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

RUNNING = [pygame.image.load(os.path.join("Assets/Dino", "DinoRun1.png")),
           pygame.image.load(os.path.join("Assets/Dino", "DinoRun2.png"))]

JUMPING = pygame.image.load(os.path.join("Assets/Dino", "DinoJump.png"))

DOWN = [pygame.image.load(os.path.join("Assets/Dino", "DinoDown1.png")),
        pygame.image.load(os.path.join("Assets/Dino", "DinoDown2.png"))]

SMALL_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus1.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus2.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus3.png"))]
LARGE_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus1.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus2.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus3.png"))]
BIRDS =        [pygame.image.load(os.path.join("Assets/Birds", "BirdWingUp.png")),
                pygame.image.load(os.path.join("Assets/Birds", "BirdWingUp.png"))]
BIRDSG =       [pygame.image.load(os.path.join("Assets/Birds", "BirdWingGroup.png"))]

BG = pygame.image.load(os.path.join("Assets/Other", "Track.png"))

FONT = pygame.font.Font('freesansbold.ttf', 20)


class Dinosaur:
    X_POS = 80
    Y_POS = 310
    JUMP_VEL = 8.5
    Y_POS_DOWN = 350

    def __init__(self, img=RUNNING[0]):
        self.image = img
        self.dino_run = True
        self.dino_jump = False
        self.dino_down = False
        self.jump_vel = self.JUMP_VEL
        self.rect = pygame.Rect(self.X_POS, self.Y_POS, img.get_width(), img.get_height())
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.step_index = 0

    def update(self):
        if self.dino_run:
            self.run()
        if self.dino_jump:
            self.jump()
        if self.dino_down:
            self.down()
        if self.step_index >= 10:
            self.step_index = 0

    def down(self):
        self.image = DOWN[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.rect.x = self.X_POS
        self.rect.y = self.Y_POS_DOWN
        self.step_index += 1
       
    def jump(self):
        self.image = JUMPING
        if self.dino_jump:
            self.rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.8
        if self.jump_vel <= -self.JUMP_VEL:
            self.dino_jump = False
            self.dino_run = True
            self.jump_vel = self.JUMP_VEL

    def run(self):
        self.image = RUNNING[self.step_index // 5]
        self.rect.x = self.X_POS
        self.rect.y = self.Y_POS
        self.step_index += 1

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.rect.x, self.rect.y))
        pygame.draw.rect(SCREEN, self.color, (self.rect.x, self.rect.y, self.rect.width, self.rect.height), 2)
        for obstacle in obstacles:
            pygame.draw.line(SCREEN, self.color, (self.rect.x + 54, self.rect.y + 12), obstacle.rect.center, 2)


class Obstacle:
    def __init__(self, image, number_of_cacti):
        self.image = image
        self.type = number_of_cacti
        self.rect = self.image[self.type].get_rect()
        self.rect.x = SCREEN_WIDTH

    def update(self):
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            obstacles.pop()

    def draw(self, SCREEN):
        SCREEN.blit(self.image[self.type], self.rect)


class SmallCactus(Obstacle):
    def __init__(self, image, number_of_cacti):
        super().__init__(image, number_of_cacti)
        self.rect.y = 325


class LargeCactus(Obstacle):
    def __init__(self, image, number_of_cacti):
        super().__init__(image, number_of_cacti)
        self.rect.y = 300

class HighBirds(Obstacle):
    def __init__(self, image, number_of_cacti):
        super().__init__(image, number_of_cacti)
        self.rect.y = 195
        # self.rect.x = self.rect.x + number_of_cacti

class LowBirds(Obstacle):
    def __init__(self, image, number_of_cacti):
        super().__init__(image, number_of_cacti)
        self.rect.y = 280
        # self.rect.x = self.rect.x + 20

class MultipleLowBirds(Obstacle):
    def __init__(self, image, number_of_cacti):
        self.type = 0
        super().__init__( image, self.type)
        self.rect.y = 280
        self.index = 0

    # def draw(self, SCREEN):
    #     if self.index >= 9:
    #         self.index = 0
    #     SCREEN.blit(self.image[self.index // 5], self.rect)
    #     self.index += 1


def remove(index):
    dinosaurs.pop(index)
    ge.pop(index)
    nets.pop(index)


def distance(pos_a, pos_b):
    dx = pos_a[0]-pos_b[0]
    dy = pos_a[1]-pos_b[1]
    return math.sqrt(dx**2+dy**2)

record = 0
def eval_genomes(genomes, config):
    global game_speed, x_pos_bg, y_pos_bg, obstacles, dinosaurs, ge, nets, points
    clock = pygame.time.Clock()
    points = 0

    obstacles = []
    dinosaurs = []
    ge = []
    nets = []

    x_pos_bg = 0
    y_pos_bg = 380
    game_speed = 20

    for genome_id, genome in genomes:
        dinosaurs.append(Dinosaur())
        ge.append(genome)
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0

    def score():
        global points, game_speed, record
        points += 1
        if points % 100 == 0:
            game_speed += 1
        text = FONT.render(f'Points:  {str(points)}', True, (0, 0, 0))
        if points >= record:
            record = points
        text_record = FONT.render(f'Record: {str(record)}', True, (0, 0, 0))
        SCREEN.blit(text, (950, 50))
        SCREEN.blit(text_record, (950, 70))

    def statistics():
        global dinosaurs, game_speed, ge
        text_1 = FONT.render(f'Dinosaurs Alive:  {str(len(dinosaurs))}', True, (0, 0, 0))
        text_2 = FONT.render(f'Generation:  {pop.generation+1}', True, (0, 0, 0))
        text_3 = FONT.render(f'Game Speed:  {str(game_speed)}', True, (0, 0, 0))

        SCREEN.blit(text_1, (50, 450))
        SCREEN.blit(text_2, (50, 480))
        SCREEN.blit(text_3, (50, 510))

    def background():
        global x_pos_bg, y_pos_bg
        image_width = BG.get_width()
        SCREEN.blit(BG, (x_pos_bg, y_pos_bg))
        SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
        if x_pos_bg <= -image_width:
            x_pos_bg = 0
        x_pos_bg -= game_speed

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        SCREEN.fill((255, 255, 255))

        for dinosaur in dinosaurs:
            dinosaur.update()
            dinosaur.draw(SCREEN)

        if len(dinosaurs) == 0:
            break

        if len(obstacles) == 0:
            rand_int = random.randint(0, 4)
            # rand_int = 4
            if rand_int == 0:
                obstacles.append(SmallCactus(SMALL_CACTUS, random.randint(0, 2)))
            elif rand_int == 1:
                obstacles.append(LargeCactus(LARGE_CACTUS, random.randint(0, 2)))
            elif rand_int == 2:
                for n in range(1, 4):
                    obstacles.append(HighBirds(BIRDS, 1))
            elif rand_int == 3:
                for n in range(1, 4):
                    obstacles.append(LowBirds(BIRDS, 1))
            elif rand_int == 4:
                obstacles.append(MultipleLowBirds(BIRDSG, 1))

        for obstacle in obstacles:
            obstacle.draw(SCREEN)
            obstacle.update()
            for i, dinosaur in enumerate(dinosaurs):
                if dinosaur.rect.colliderect(obstacle.rect):
                    # ge[i].fitness -= 1 
                    ge[i].fitness -= 1 #points
                    remove(i)
                else:
                    ge[i].fitness += 2 #points

        for i, dinosaur in enumerate(dinosaurs):
            # print(f"1: {obstacle.rect.midtop} 2: {obstacle.rect.midbottom} 3: {dinosaur.rect.x} {dinosaur.rect.y}")
            output = nets[i].activate((dinosaur.rect.y,
                                       distance((dinosaur.rect.x, dinosaur.rect.y),
                                        obstacle.rect.midtop),
                                        distance((dinosaur.rect.y, dinosaur.rect.y),
                                        obstacle.rect.midtop),
                                        game_speed
                                        ))
            print(f"outpu: {output}")
            if output[0] >= 0 and output[1] >= 0 and dinosaur.rect.y >= dinosaur.Y_POS: # not dinosaur.dino_jump:
                dinosaur.dino_down = False
                dinosaur.dino_run = False
                dinosaur.dino_jump = True
            elif output[0] <= 0 and output[1] <= 0 and not dinosaur.dino_jump:
                dinosaur.dino_down = True
                dinosaur.dino_run = False
                dinosaur.dino_jump = False                
            elif not (dinosaur.dino_jump or dinosaur.dino_down):
                dinosaur.dino_down = False
                dinosaur.dino_run = True
                dinosaur.dino_jump = False
                
        statistics()
        score()
        background()
        clock.tick(30)
        pygame.display.update()

network_dir = 'network'
network_prefix = 'neat-checkpoint-'

def last_network_checkpoint():
    list_of_files = glob.glob(f'{network_dir}/*')
    lastest_file = max(list_of_files, key=os.path.getctime)
    return lastest_file

# Setup the NEAT Neural Network
def run(config_path, restore_network=True):
    global pop
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )
    restore_network = False
    print(f"Restore Network: {restore_network}")
    if restore_network == True:
        pop = neat.Checkpointer.restore_checkpoint(last_network_checkpoint())
    else:
        pop = neat.Population(config, initial_state=None)

    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)
    pop.add_reporter(neat.Checkpointer(1, 5,f'{network_dir}/{network_prefix}'))

    pop.run(eval_genomes, 300)
    # pop.run(eval_genomes)

    stats.save()
    print(f"Recorded: {record}")
    


if __name__ == '__main__':
    restore_network = False
    if len(sys.argv) > 2:
        restore_network = True
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    run(config_path, restore_network)
