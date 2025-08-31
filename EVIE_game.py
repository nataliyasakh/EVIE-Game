import pygame, sys, random, math, asyncio

# Configuration
WIDTH, HEIGHT = 1024, 576
FPS = 60
INSTR_DURATION = 12000  # 12 seconds for instruction screens

# Colors
WHITE        = (255,255,255)
BLACK        = (0,0,0)
SKY_TOP      = (180,230,255)
SKY_BOTTOM   = (255,255,255)
MILK_BG      = (200,220,255)
MILK_FILL    = (255,255,245)
BAR_BG       = (30,30,60)
BUTTON_BG    = (50,100,200)
BUTTON_HOVER = (100,150,250)
PARTICLE_COL = (255,200,100)
ACID_COLOR   = (255,80,80)
EV_COLOR     = (100,200,255)
EV_MATCHED   = (120,255,180)
TRAP_COLOR   = (200,140,200)
GOLGI_COLOR  = (255,200,120)
SUGAR_COLORS = {"mannose":(240,240,130),"glucose":(230,230,250)}

pygame.init()
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("rEVitalyze: The GlycoQuest")
clock = pygame.time.Clock()

# Fonts
F_TITLE = pygame.font.SysFont("trebuchet ms",52,bold=True)
F_LARGE = pygame.font.SysFont("trebuchet ms",36,bold=True)
F_MED   = pygame.font.SysFont("trebuchet ms",28)
F_SM    = pygame.font.SysFont("trebuchet ms",22)
F_INFO  = pygame.font.SysFont("trebuchet ms",20,italic=True)

# Global state
scene = "PROJECT_INTRO"
score = 0
particles = []
level_scores = {}

# Helpers
def draw_gradient(top,bottom):
    for y in range(HEIGHT):
        t=y/HEIGHT
        c=(
            int(top[0]*(1-t)+bottom[0]*t),
            int(top[1]*(1-t)+bottom[1]*t),
            int(top[2]*(1-t)+bottom[2]*t)
        )
        pygame.draw.line(screen,c,(0,y),(WIDTH,y))

def draw_text(txt,x,y,font,color=BLACK,center=True):
    surf=font.render(txt,True,color)
    rect=surf.get_rect(center=(x,y)) if center else surf.get_rect(topleft=(x,y))
    screen.blit(surf,rect)

def draw_button(txt,x,y,w,h,action=None):
    mx,my=pygame.mouse.get_pos()
    over=x<mx<x+w and y<my<y+h
    col=BUTTON_HOVER if over else BUTTON_BG
    pygame.draw.rect(screen,col,(x,y,w,h),border_radius=8)
    draw_text(txt,x+w//2,y+h//2,F_MED,WHITE)
    if over and pygame.mouse.get_pressed()[0]:
        pygame.time.delay(150)
        if action: action()

def emit_particles(x,y,count=20):
    for _ in range(count):
        particles.append([[x,y],[random.uniform(-2,2),random.uniform(-5,-1)],random.randint(4,8)])

def update_particles(dt):
    for p in particles[:]:
        p[0][0]+=p[1][0]; p[0][1]+=p[1][1]
        p[2]-=dt*0.015; p[1][1]+=0.1
        if p[2]<=0: particles.remove(p)

def draw_particles():
    for p in particles:
        pygame.draw.circle(screen,PARTICLE_COL,(int(p[0][0]),int(p[0][1])),int(p[2]))

class LevelBase:
    def __init__(self):
        self.popups=[]
    def popup(self,text):
        self.popups.append([text,3000])
    def common_tick(self,dt):
        for p in self.popups: p[1]-=dt
        self.popups=[p for p in self.popups if p[1]>0]
    def common_draw(self):
        y=HEIGHT-80
        for text,_ in self.popups:
            panel=pygame.Surface((WIDTH,60),pygame.SRCALPHA)
            pygame.draw.rect(panel,(255,255,255,230),panel.get_rect(),border_radius=8)
            t=F_SM.render(text,True,(30,30,60))
            panel.blit(t,t.get_rect(center=(WIDTH//2,30)))
            screen.blit(panel,(0,y)); y-=70

class ProjectIntro(LevelBase):
    def update(self,dt,evs):
        global scene
        for e in evs:
            if e.type==pygame.QUIT: pygame.quit();sys.exit()
            if e.type==pygame.MOUSEBUTTONDOWN:
                sx,sy,sw,sh=WIDTH//2-100,HEIGHT-160,200,80
                if sx<e.pos[0]<sx+sw and sy<e.pos[1]<sy+sh:
                    scene="INSTR1"
    def draw(self):
        screen.fill(WHITE)
        draw_text("Read Instructions",WIDTH//2,80,F_TITLE)
        desc1=["The congenital disorders of glycosylation (CDGs) are rare metabolic",
               "diseases caused by errors in sugar addition to proteins/lipids.",
               "Our team engineered probiotic E. coli to package functional",
               "PMM2 into EVs for oral delivery via milk."]
        desc2=["This game simulates that journey: you’ll 'drink' fortified milk,",
               "dodge stomach conditions, deliver EVs to receptors, guide enzyme,",
               "and assemble glycans to restore glycosylation—mirroring our lab."]
        y=150
        for line in desc1: draw_text(line,WIDTH//2,y,F_MED); y+=30
        y=300
        for line in desc2: draw_text(line,WIDTH//2,y,F_MED); y+=30
        # Start and Quit
        draw_button("Start Playing",WIDTH//2-100,HEIGHT-160,200,80,action=lambda:setattr(sys.modules[__name__],'scene',"INSTR1"))
        draw_button("Quit",WIDTH-120,50,100,40,action=sys.exit)

class Instr(LevelBase):
    def __init__(self,text,next_scene):
        super().__init__()
        self.text=text; self.next_scene=next_scene; self.timer=INSTR_DURATION
    def update(self,dt,evs):
        global scene
        self.timer-=dt
        for e in evs:
            if e.type==pygame.QUIT: pygame.quit();sys.exit()
            if e.type==pygame.MOUSEBUTTONDOWN:
                sx,sy,sw,sh=WIDTH//2-100,HEIGHT-160,200,80
                if sx<e.pos[0]<sx+sw and sy<e.pos[1]<sy+sh:
                    scene=self.next_scene
        if self.timer<=0: scene=self.next_scene
    def draw(self):
        screen.fill(WHITE)
        draw_text("Instructions",WIDTH//2,80,F_TITLE)
        lines=self.text.split("\n")
        y=150
        for L in lines: draw_text(L,WIDTH//2,y,F_MED); y+=40
        draw_button("Quit",WIDTH-120,50,100,40,action=sys.exit)
        draw_button("Skip to Game",WIDTH//2-100,HEIGHT-160,200,80,
                    action=lambda:setattr(sys.modules[__name__],'scene',self.next_scene))

class Level1(LevelBase):
    def __init__(self):
        super().__init__()
        self.fill=0; self.glass=pygame.Rect(WIDTH//2-70,150,140,300)
        self.info=pygame.Rect(WIDTH-158,HEIGHT-78,36,36)
    def update(self,dt,evs):
        global scene,score,level_scores
        for e in evs:
            if e.type==pygame.QUIT: pygame.quit();sys.exit()
            if e.type==pygame.MOUSEBUTTONDOWN:
                if self.glass.collidepoint(e.pos):
                    self.fill=min(300,self.fill+60); emit_particles(*e.pos)
                    if self.fill>=300: level_scores['L1']=score; scene="INSTR2"
                elif self.info.collidepoint(e.pos):
                    self.popup("Sip the milk to receive EVs carrying PMM2.")
        update_particles(dt)
    def draw(self):
        draw_gradient(SKY_TOP,SKY_BOTTOM)
        pygame.draw.rect(screen,BAR_BG,(0,0,WIDTH,40))
        draw_text(f"Score: {int(score)}",90,20,F_MED,WHITE)
        pygame.draw.rect(screen,MILK_BG,self.glass,border_radius=24)
        inner=self.glass.inflate(-12,-12)
        fill_rect=pygame.Rect(inner.x,inner.bottom-self.fill,inner.width,self.fill)
        pygame.draw.rect(screen,MILK_FILL,fill_rect,border_radius=16)
        draw_text("Click Glass to Drink",WIDTH//2,100,F_LARGE)
        pygame.draw.circle(screen,(200,200,255),self.info.center,18)
        draw_text("i",self.info.centerx,self.info.centery,F_INFO)
        draw_button("Quit",WIDTH-120,50,100,40,action=sys.exit)
        self.common_draw(); draw_particles()

class Level2(LevelBase):
    def __init__(self):
        super().__init__()
        self.x=140; self.y=HEIGHT//2; self.vx=0; self.vy=0
        self.acids=[(random.randint(200,WIDTH-40),random.randint(60,HEIGHT-140)) for _ in range(6)]
        self.timer=10000
    def update(self,dt,evs):
        global scene,score,level_scores
        keys=pygame.key.get_pressed()
        self.vx=(keys[pygame.K_RIGHT]-keys[pygame.K_LEFT])*4
        self.vy=(keys[pygame.K_DOWN]-keys[pygame.K_UP])*4
        self.x=max(40,min(WIDTH-40,self.x+self.vx))
        self.y=max(40,min(HEIGHT-40,self.y+self.vy))
        self.timer-=dt; score+=dt*0.001
        for ax,ay in self.acids:
            if abs(ax-self.x)<24 and abs(ay-self.y)<24: self.timer=0
        if self.timer<=0: level_scores['L2']=int(score); scene="INSTR3"
    def draw(self):
        draw_gradient((240,240,210),(180,200,150))
        pygame.draw.rect(screen,BAR_BG,(0,0,WIDTH,40))
        draw_text(f"Score: {int(score)}",90,20,F_MED,WHITE)
        for ax,ay in self.acids:
            dy=4*math.sin(pygame.time.get_ticks()/400+ax)
            pygame.draw.ellipse(screen,ACID_COLOR,(ax,ay+dy,24,36))
        pygame.draw.rect(screen,EV_COLOR,(self.x-20,self.y-20,40,40),border_radius=8)
        draw_text("Use ARROW KEYS to Dodge Acid",WIDTH//2,60,F_LARGE)
        draw_button("Quit",WIDTH-120,50,100,40,action=sys.exit)

class Level3(LevelBase):
    def __init__(self):
        super().__init__()
        self.rec=pygame.Rect(WIDTH-200,HEIGHT//2-60,140,120)
        self.ves=[{'x':140+i*120,'y':120+90*(i%2),'drag':False,'match':False} for i in range(4)]
    def update(self,dt,evs):
        global scene,score,level_scores
        for e in evs:
            if e.type==pygame.QUIT: pygame.quit();sys.exit()
            if e.type==pygame.MOUSEBUTTONDOWN:
                for v in self.ves:
                    if not v['match'] and (e.pos[0]-v['x'])**2+(e.pos[1]-v['y'])**2<900:
                        v['drag']=True; break
            if e.type==pygame.MOUSEBUTTONUP:
                for v in self.ves:
                    if v['drag']:
                        v['drag']=False
                        if self.rec.collidepoint(v['x'],v['y']):
                            v['match']=True; score+=5
            if e.type==pygame.MOUSEMOTION:
                for v in self.ves:
                    if v['drag']: v['x'],v['y']=e.pos
        if all(v['match'] for v in self.ves): level_scores['L3']=int(score); scene="INSTR4"
    def draw(self):
        draw_gradient((200,230,255),(150,200,255))
        pygame.draw.rect(screen,BAR_BG,(0,0,WIDTH,40))
        draw_text(f"Score: {int(score)}",90,20,F_MED,WHITE)
        pygame.draw.rect(screen,(160,200,240),self.rec,border_radius=16)
        for v in self.ves:
            c=EV_MATCHED if v['match'] else EV_COLOR
            pygame.draw.circle(screen,c,(int(v['x']),int(v['y'])),28)
        draw_text("Drag EVs to Receptor",WIDTH//2,60,F_LARGE)
        draw_button("Quit",WIDTH-120,50,100,40,action=sys.exit)

class Level4(LevelBase):
    def __init__(self):
        super().__init__()
        self.x=80; self.y=HEIGHT//2; self.speed=5
        self.traps=[pygame.Rect(random.randint(260,760),random.randint(120,400),30,100) for _ in range(4)]
    def update(self,dt,evs):
        global scene,score,level_scores
        keys=pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]: self.x+=self.speed
        if keys[pygame.K_LEFT]:  self.x-=self.speed
        if keys[pygame.K_UP]:    self.y-=self.speed
        if keys[pygame.K_DOWN]:  self.y+=self.speed
        self.x=max(20,min(WIDTH-20,self.x)); self.y=max(20,min(HEIGHT-20,self.y))
        for t in self.traps:
            if t.collidepoint(self.x,self.y):
                self.x=80; self.y=HEIGHT//2; score+=2
        if self.x>WIDTH-140 and abs(self.y-HEIGHT//2)<60:
            level_scores['L4']=int(score); scene="INSTR5"
    def draw(self):
        draw_gradient((250,215,250),(220,170,220))
        pygame.draw.rect(screen,BAR_BG,(0,0,WIDTH,40))
        draw_text(f"Score: {int(score)}",90,20,F_MED,WHITE)
        for t in self.traps: pygame.draw.rect(screen,TRAP_COLOR,t,border_radius=8)
        pygame.draw.ellipse(screen,GOLGI_COLOR,(WIDTH-140,HEIGHT//2+20,100,120))
        pygame.draw.circle(screen,(140,110,240),(int(self.x),int(self.y)),28)
        draw_text("Reach the Golgi",WIDTH//2,60,F_LARGE)
        draw_button("Quit",WIDTH-120,50,100,40,action=sys.exit)

class Level5(LevelBase):
    def __init__(self):
        super().__init__()
        self.seq=["mannose","glucose","mannose","glucose"]
        self.choice=[]; self.timer=15000; self.done=False
    def update(self,dt,evs):
        global scene,score,level_scores
        if not self.done:
            self.timer-=dt
            for e in evs:
                if e.type==pygame.KEYDOWN and len(self.choice)<len(self.seq):
                    if e.key==pygame.K_1: self.choice.append("mannose")
                    if e.key==pygame.K_2: self.choice.append("glucose")
            if len(self.choice)==len(self.seq):
                if self.choice==self.seq: score+=10
                self.done=True
        if self.done and self.timer<14500: level_scores['L5']=int(score); scene="VICTORY"
    def draw(self):
        draw_gradient((255,255,240),(230,230,210))
        pygame.draw.rect(screen,BAR_BG,(0,0,WIDTH,40))
        draw_text(f"Score: {int(score)}",90,20,F_MED,WHITE)
        base=200
        for i,s in enumerate(self.seq):
            pygame.draw.circle(screen,SUGAR_COLORS[s],(base+i*160,200),40)
            draw_text(s[:3].upper(),base+i*160,200,F_SM)
        for i,c in enumerate(self.choice):
            col=(160,250,130) if c==self.seq[i] else (255,120,120)
            pygame.draw.circle(screen,col,(base+i*160,330),32)
        draw_text(f"Time: {max(0,int(self.timer/1000))}s",WIDTH//2,60,F_LARGE)
        draw_button("Quit",WIDTH-120,50,100,40,action=sys.exit)

class Victory(LevelBase):
    def update(self,dt,evs):
        for e in evs:
            if e.type in (pygame.QUIT,pygame.KEYDOWN): pygame.quit();sys.exit()
    def draw(self):
        draw_gradient((215,255,225),(170,230,200))
        draw_text("Victory!",WIDTH//2,200,F_TITLE,(20,120,20))
        draw_text("Final Score: "+str(int(score)),WIDTH//2,280,F_LARGE)
        y=340
        for lvl,pts in level_scores.items():
            draw_text(f"{lvl}: {pts}",WIDTH//2,y,F_MED); y+=40
        draw_button("Quit",WIDTH-120,50,100,40,action=sys.exit)

scenes={
    "PROJECT_INTRO":ProjectIntro(),
    "INSTR1":Instr("Level 1:\nClick glass to drink EV-fortified milk.","LEVEL1"),
    "LEVEL1":Level1(),
    "INSTR2":Instr("Level 2:\nUse ARROW KEYS to dodge acid blobs.","LEVEL2"),
    "LEVEL2":Level2(),
    "INSTR3":Instr("Level 3:\nDrag EVs to the receptor.","LEVEL3"),
    "LEVEL3":Level3(),
    "INSTR4":Instr("Level 4:\nMove enzyme with ARROW KEYS to reach Golgi.","LEVEL4"),
    "LEVEL4":Level4(),
    "INSTR5":Instr("Level 5:\nPress 1=mannose,2=glucose in sequence.","LEVEL5"),
    "LEVEL5":Level5(),
    "VICTORY":Victory()
}

async def main():
    global scene
    while True:
        dt=clock.tick(FPS)
        evs=pygame.event.get()
        obj=scenes.get(scene)
        if obj:
            obj.update(dt,evs)
            obj.common_tick(dt)
            obj.draw()
        pygame.display.flip()
        await asyncio.sleep(0)

if __name__=="__main__":
    asyncio.run(main())
