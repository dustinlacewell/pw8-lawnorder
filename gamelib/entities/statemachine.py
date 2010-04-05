from gamelib.geometry import Vec2D, Entity, sign

class StateMachine(Entity):

    class State(Entity):
        def __init__(self, pos=Vec2D(0, 0)):
            super(StateMachine.State, self).__init__(pos)
        def update(_self, self, dt, t, *args, **kwargs):
            pass
        def render(_self, self, screen, dt, t, *args, **kwargs):
            pass
        def collision_response(_self, self, other):
            pass
        def enter(_self, self):
            pass
        def leave(_self, self):
            pass
        def activate(_self, self, player, *args, **kwargs):
            pass
        def handle_event(_self, self, event):
            pass

    def __init__(self, pos_vec, start_state, *args, **kwargs):
        super(StateMachine, self).__init__(pos_vec)
        self.spr = None
        self.cur_state = None
        self.change_state(start_state)
        self.facing = 1
        

    def change_state(self, new_state):
        if self.cur_state:
            self.cur_state.leave(self)
        self.cur_state = new_state
        self.cur_state.enter(self)

    def update(self, dt, t, *args, **kwargs):
        self.cur_state.update(self, dt, t, *args, **kwargs)
        dir = sign(self.vel.x)
        if dir:
            self.facing = dir

    def activate(self, player=None, *args,  **kwargs):
        self.cur_state.activate(self, player, *args, **kwargs)

    def render(self, screen, dt, t, *args, **kwargs):
        self.cur_state.render(self, screen, dt, t, *args, **kwargs)

    def collision_response(self, other):
        self.cur_state.collision_response(self, other)
        