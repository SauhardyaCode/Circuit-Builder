import pygame
from tkinter import messagebox as msg
from pygame.locals import *
import gates

pygame.init()
circuit = gates.Circuits()

clock = pygame.time.Clock()
FPS = 100
screen = pygame.display.set_mode((0,0), 1)
WIDTH = screen.get_width()
HEIGHT = screen.get_height()
BGCOLOR = (60,60,60)
CNV_size = (1450, 800)
TSK_height = 50

menu_btn=None
menu_toggle=0
menu_options = []

all_circuits = []
task_circuits = [circuit.AND().get_data(), circuit.NOT().get_data()]
task_circuits_rect = []

class Button():
    def __init__(self, bg, text, pos, height, pad=30):
        global menu_btn
        self.bg=bg
        self.fg=(255,255,255)
        self.text = text
        self.pos = pos
        self.font = pygame.font.SysFont('gothalic',30)
        self.label = self.font.render(self.text,1,self.fg,self.bg)
        self.block = self.label.get_rect()
        self.block.w+=pad
        self.block.h = height
        self.block.topleft=self.pos
        if self.text=="MENU":
            menu_btn = self.block
    
    def draw(self):
        self.highlight()
        screen.blit(self.label,(self.block.centerx-self.label.get_width()/2,self.block.centery-self.label.get_height()/2))
        if self.block.left<0:
            self.block.left=0
        if self.block.top<0:
            self.block.top=0
        if self.block.right>WIDTH:
            self.block.right=WIDTH
        if self.block.bottom>HEIGHT:
            self.block.bottom=HEIGHT
    
    def highlight(self):
        if self.block.collidepoint(pygame.mouse.get_pos()):
            if self.text == "MENU":
                bg=(80, 112, 162)
            else:
                bg=(100,100,100)
            pygame.draw.rect(screen,bg,self.block)
        else:
            pygame.draw.rect(screen,self.bg,self.block)
        self.label = self.font.render(self.text,1,self.fg)

class TaskBar():
    def __init__(self, blocks:list):
        self.blocks = blocks
        self.gap = 5
        self.height = TSK_height

    def boundary(self):
        color=(30,30,30)
        outline = pygame.rect.Rect(0,HEIGHT-self.height,WIDTH,self.height)
        pygame.draw.rect(screen,color,outline)

    def create(self):
        self.boundary()
        Y = HEIGHT-self.height+self.gap
        menu = Button((40, 82, 122),"MENU",(self.gap,Y),self.height-2*self.gap)

        widths = [menu.block.w]
        for x in self.blocks:
            ic = Button(BGCOLOR,x[0],(0,0),0)
            widths.append(ic.block.w)

        for i,x in enumerate(self.blocks):
            ic = Button(BGCOLOR,x[0],(sum(widths[:i+1])+self.gap*(i+2),Y),self.height-2*self.gap)
            if not ic in task_circuits_rect:
                task_circuits_rect.append(ic.block)
            ic.draw()

        menu.draw()

class Menu():
    def __init__(self, bottom, size=(280,180)):
        self.font = pygame.font.SysFont("verdana",20)
        self.size = size
        self.bottom = bottom
    
    def create(self):
        global menu_options
        options = [("NEW","Ctrl+N"),("SAVE","Ctrl+S"),("LIBRARY","Ctrl+L"),("QUIT","Ctrl+Q")]
        menu_options=[]
        for i,x in enumerate(options[::-1]):
            a,b=x
            text = self.font.render(a,1,(0,0,0))
            text2 = self.font.render(b,1,(0,0,0))
            rect = text.get_rect()
            rect.w=self.size[0]
            rect.h+=10
            rect.bottom = self.bottom-i*rect.h
            if rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(screen,(95, 189, 255),rect)
            else:
                pygame.draw.rect(screen,(255,255,255),rect)
            screen.blit(text,(rect.x+15,rect.centery-text.get_height()/2))
            screen.blit(text2,(rect.right-15-text2.get_width(),rect.centery-text.get_height()/2))
            menu_options.insert(0,(rect,eval(f"K_{b[-1].lower()}")))
    
    def click(self):
        global menu_toggle
        for i,x in enumerate(menu_options):
            if x[0].collidepoint(pygame.mouse.get_pos()) and menu_toggle:
                if i==0:
                    self.new()
                elif i==1:
                    self.save()
                elif i==2:
                    self.library()
                else:
                    self.quit()
    
    def press(self):
        for x in menu_options:
            if KMOD_CTRL:
                if ev.key==x[1]:
                    if x[1]==K_n:
                        self.new()
                    if x[1]==K_s:
                        self.save()
                    if x[1]==K_l:
                        self.library()
                    else:
                        self.quit()
    def new(self):
        pass
    def save(self):
        pass
    def library(self):
        pass
    def quit(self):
        if msg.askyesno("QUIT","Do you want to quit?"):
            pygame.quit()
            exit()

class Canvas():
    def __init__(self, task_ht, size=CNV_size):
        self.outline = pygame.rect.Rect((WIDTH-size[0])/2,(HEIGHT-task_ht-size[1])/2,*size)
        self.fill = pygame.rect.Rect((WIDTH-size[0])/2,(HEIGHT-task_ht-size[1])/2,*size)
    
    def create(self):
        pygame.draw.rect(screen,(50,50,50),self.fill)
        pygame.draw.rect(screen,(100,100,100),self.outline,4)

class IO():
    def __init__(self, height):
        self.left = pygame.rect.Rect(0,0,25,height-20)
        self.right = pygame.rect.Rect(0,0,25,height-20)
        self.left.centery=height//2
        self.right.centery=height//2
        self.right.right=WIDTH
    
    def create(self):
        pygame.draw.rect(screen,(40,40,40),self.left)
        pygame.draw.rect(screen,(40,40,40),self.right)

class Circuits():
    def __init__(self, text, color, func:list, pad=40):
        self.color=color
        self.func = func
        self.font = pygame.font.SysFont("robota",35)
        self.label = self.font.render(text,1,(255,255,255))
        self.pad=pad

        self.rect = self.label.get_rect()
        self.rect.w+=pad
        self.outline = pygame.rect.Rect(0,0,self.rect.w,self.rect.h)
        self.rect.center = pygame.mouse.get_pos()

        self.PINS = [[],[]]
        self.selected = 1
        self.drag = 1
        self.clicks = 0
        self.do = 1

    
    def create(self):
        self.outline.center = self.rect.center
        outline = pygame.rect.Rect(0,0,self.rect.w+30,self.rect.h+20)
        if self.selected:
            outline.center=self.rect.center
            pygame.draw.rect(screen,(70,70,70),outline)
            pygame.draw.rect(screen,[x+50 if x<=205 else x for x in self.color],self.rect)
            pygame.draw.rect(screen,(0,0,0),self.outline,1)
        else:
            pygame.draw.rect(screen,self.color,self.rect)
            pygame.draw.rect(screen,(100,100,100),self.outline,1)
        screen.blit(self.label,(self.rect.centerx-self.label.get_width()/2,self.rect.centery-self.label.get_height()/2))
        self.pins()
        self.move()
    
    def pins(self, dia=20, gap=3):
        if max(self.func)==1:
            gap+=self.pad//5
        self.gap = gap
        height = gap*(max(self.func)+1)+dia*(max(self.func))
        self.rect.h = height
        self.outline.h = height
        for x,f in enumerate(self.func):
            for i in range(f):
                pin = pygame.rect.Rect(0,0,dia,dia)
                if x:
                    pin.centerx = self.rect.right
                else:
                    pin.centerx = self.rect.left
                if not f==max(self.func):
                    gap=(height-f*dia)//(f+1)
                else:
                    gap = self.gap
                pin.y = self.rect.top+gap*(i+1)+dia*i
                self.PINS[x].append(pin)
                if self.selected:
                    pin_col = (40,40,40)
                else:
                    pin_col = (0,0,0)
                if pin.collidepoint(pygame.mouse.get_pos()):
                    pygame.draw.rect(screen,(200,200,200),pin,0,dia//2)
                else:
                    pygame.draw.rect(screen,pin_col,pin,0,dia//2)
        
    def move(self):
        if self.selected:
            if self.drag:
                # if self.clicks==1:
                #     self.do=1
                # if self.do:
                    self.rect.center = pygame.mouse.get_pos()
            else:
                if self.rect.left<(WIDTH-CNV_size[0])/2 or self.rect.right>(WIDTH+CNV_size[0])/2 or self.rect.top<((HEIGHT-TSK_height)-CNV_size[1])/2 or self.rect.bottom>((HEIGHT-TSK_height)+CNV_size[1])/2:
                    self.selected=1
                    self.drag=1
                    self.do=1

class App():
    def __init__(self):
        self.taskbar = TaskBar(task_circuits)
        self.canvas = Canvas(self.taskbar.height)
        self.io = IO(HEIGHT-self.taskbar.height)
        self.menu = Menu(HEIGHT-self.taskbar.height)
        self.menu.create() #just to enable shortcut keys
    
    def create(self):
        global menu_toggle
        self.canvas.create()
        self.io.create()
        for x in all_circuits:
            x.create()
        self.taskbar.create()
        if menu_toggle:
            self.menu.create()

# _and = Circuits(*circuit.AND().get_data())
# all_circuits.append(_and)
app = App()

while True:
    screen.fill(BGCOLOR)
    app.create()

    for ev in pygame.event.get():
        if ev.type==QUIT:
            app.menu.quit()
        elif ev.type==MOUSEBUTTONDOWN:
            for x in all_circuits:
                for pin in x.PINS[0]+x.PINS[1]:
                    if pin.collidepoint(pygame.mouse.get_pos()):
                        x.selected=0
                        break
                else:
                    if x.selected:
                        if x.rect.collidepoint(pygame.mouse.get_pos()):
                            x.drag=1
                            # x.clicks+=1
                    #     elif not x.rect.collidepoint(pygame.mouse.get_pos()) or pygame.mouse.get_pressed()[2]:
                    #         x.selected=0
                    # else:
                    #     if x.rect.collidepoint(pygame.mouse.get_pos()):
                    #         x.selected=1
                print(x.selected,x.drag,x.do)
                                
                            
        elif ev.type==MOUSEBUTTONUP:
            app.menu.click()
            if menu_btn.collidepoint(pygame.mouse.get_pos()):
                menu_toggle=1-menu_toggle
            else:
                menu_toggle=0
            for x in all_circuits:
                for pin in x.PINS[0]+x.PINS[1]:
                    if pin.collidepoint(pygame.mouse.get_pos()):
                        x.selected=0
                        break
                else:
                    if x.selected:
                        if not x.rect.collidepoint(pygame.mouse.get_pos()) or pygame.mouse.get_pressed()[2]:
                            x.selected=0
                        else:
                            x.drag=0
                    else:
                        if x.rect.collidepoint(pygame.mouse.get_pos()):
                            x.selected=1
                # x.clicks=0
                # x.do=0

            for i in range(len(task_circuits)):
                if task_circuits_rect[i].collidepoint(pygame.mouse.get_pos()):
                    all_circuits.append(Circuits(*task_circuits[i]))


        elif ev.type==KEYDOWN:
            app.menu.press()
            
    pygame.display.update()
    clock.tick(FPS)


#drag drop error!