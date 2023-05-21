from ursina import Ursina, Entity, raycast, EditorCamera, held_keys, Sky, Text, color
from ursina.shaders import basic_lighting_shader
import random

app = Ursina()
EditorCamera()


air_friction = .02
gravity = .05
terminal_velocity = 1


class PhysObject:
    def __init__(self):
        self.velx, self.vely, self.velz = (0, 0, 0)
        self.entity = Entity()

    def update(self):
        if self.vely < terminal_velocity:
            self.vely -= gravity


        self.cast = raycast(self.entity.position, self.entity.down, 1)
        if self.cast.hit:
            if self.vely < 0:
                self.vely = 0


        self.cast = raycast(self.entity.position, self.entity.up, 5)
        if self.cast.hit:
            self.vely = 0
            x_, y_, z_ = self.cast.world_point
            self.entity.y = y_ + 1
        
        self.entity.y += self.vely
        self.entity.x += self.velx
        self.entity.z += self.velz

        def stepto(val, step, target):
            val_ = val

            if val > target:
                val_ -= step
            if val < target:
                val_ += step

            return val_

        self.velx = stepto(self.velx, air_friction, 0)
        self.vely = stepto(self.vely, air_friction, 0)
        self.velz = stepto(self.velz, air_friction, 0)
    
    def force(self, x, y, z):
        self.velx += x
        self.vely += y
        self.velz += z


rabbits = []
class Rabbit:
    def __init__(self, interval, direction, startingposition):
        self.interval = interval
        self.direction = direction
        self.startingposition = startingposition

        self.physobject = PhysObject()
        self.physobject.entity.position = self.startingposition
        self.entity = Entity(model="rabbit", texture="rabbit", parent=self.physobject.entity, shader=basic_lighting_shader, double_sided=True)
        self.timer = 0
        self.is_alive = True

        self.best_y = 0

    def update(self):
        if self.is_alive:
            if self.entity.parent.y < -200:
                self.is_alive = False
                
            else:

                self.physobject.update()

                if self.physobject.entity.y > self.best_y:
                    self.best_y = self.physobject.entity.y

                self.timer += 1
                if self.timer == self.interval:
                    self.timer = 0

                    self.entity.rotation_y = self.direction

                    vel_x, vel_y, vel_z = self.entity.forward
                    self.physobject.force(vel_x, 1, vel_z)
    
    def respawn(self, interval, direction, startingposition):
        self.is_alive = True
        self.interval = interval
        self.direction = direction
        self.startingposition = startingposition
        self.timer = 0

        self.physobject.velx, self.physobject.vely, self.physobject.velz = (0, 0, 0)
        self.physobject.entity.position = self.startingposition
        self.entity.position = (0, 0, 0)
        self.entity.rotation = (0, 0, 0)

for i in range(20):
    rabbits.append(Rabbit(random.randint(0, 360), random.randint(100, 300), (0, 0, 0)))

def mutate(value, strength):
    rng = range(value - strength, value + strength)
    return rng[random.randint(0, len(rng) - 1)]

timer = 0
generation = 1
mutation_strength = 10
def update():
    global timer, generation, mutation_strength, rabbits

    if held_keys["up arrow"]:
        plane.y += .1
    if held_keys["down arrow"]:
        plane.y -= .1

    timer += 1

    for r in rabbits:
        r.update()
    
    if timer == 1500:
        generation += 1
        gen_display.text = f"Generation: {generation}"

        timer = 0
        
        best_y_global = 0
        best = None

        for r in rabbits:
            interval, direction, best_y, starting_position = r.interval, r.direction, r.best_y, r.startingposition
            if best_y > best_y_global:
                best = {"interval":interval, "direction":direction, "startingposition":starting_position}
        
        for i in range(len(rabbits)):
            if best:
                print(best)
                
                direction = mutate(best["direction"], mutation_strength)

                interval = mutate(best["interval"], mutation_strength)

                #sx, sy, sz = best["startingposition"]
                #sx = mutate(sx, mutation_strength)
                #sy = mutate(sy, mutation_strength)
                #sz = mutate(sz, mutation_strength)
                #starting_position = sx, sy, sz
                starting_position = (0, 0, 0)
            else:
                direction = random.randint(0, 360)

                interval = random.randint(100, 300)

                starting_position = (0, 0, 0)

            rabbits[i].respawn(interval, direction, starting_position)

map_collider = Entity(model="map_collision", scale=20, y=-10, collider="mesh", visible=False)
plane = Entity(model="map", scale=20, texture="grass", y=-10, double_sided=True)

gen_display = Text(f"Generation: {generation}", color=color.black, position=(-.85, .45))

Sky()

app.run()