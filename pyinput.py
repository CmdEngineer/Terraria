import struct
import threading

file_in = open("/dev/input/event0", "rb")

MOUSE_BUTTON_TYPE = 1
MOUSE_PRESS_VALUE = 1
MOUSE_LEFT_CLICK_CODE = 272
MOUSE_RIGHT_CLICK_CODE = 273
MOUSE_SCROLL_CODE = 8
MOUSE_SCROLL_UP_VALUE = 1
MOUSE_SCROLL_DOWN_VALUE = -1

MOUSE_MOVE_TYPE = 2
MOUSE_MOVE_RL_CODE = 0
MOUSE_MOVE_UD_CODE = 1

CONTROLLER_MOVE_TYPE = 3
CONTROLLER_BUTTON_TYPE = 1
CONTROLLER_PRESS_VALUE = 1
CONTROLLER_RELEASE_VALUE = 0
CONTROLLER_A_CODE = 304
CONTROLLER_B_CODE = 305
CONTROLLER_Y_CODE = 308
CONTROLLER_X_CODE = 307
CONTROLLER_PRESS_RIGHT_JOYSTICK_CODE = 318
CONTROLLER_PRESS_LEFT_JOYSTICK_CODE = 317
CONTROLLER_LB_CODE = 310
CONTROLLER_RB_CODE = 311
CONTROLLER_LT_CODE = 2
CONTROLLER_RT_CODE = 5
CONTROLLER_PAD_UD_CODE = 17
CONTROLLER_PAD_RL_CODE = 16
CONTROLLER_RJ_CODES = 3, 4
CONTROLLER_LJ_CODES = 0, 1

class Manager():
    def __init__(self):
        self.running = True
    
    def stop(self):
        self.running = False

class Mouse():
    def __init__(self):
        self.mx = 0
        self.my = 0
        self.w = 7 * 128
        self.h = 7 * 128
    def right_click_func(self): pass
    def left_click_func(self): pass
    def scroll_up_func(self): pass
    def scroll_down_func(self): pass
    def move_func(self): pass

    def set_right_click(self, func):
        self.right_click_func = func

    def set_left_click(self, func):
        self.left_click_func = func

    def set_scroll_up(self, func):
        self.scroll_up_func = func

    def set_scroll_down(self, func):
        self.scroll_down_func = func

    def set_move(self, func):
        self.move_func = func

    def get_position(self):
        return self.mx, self.my
    
    def get_pixel_x(self):
        return self.mx // 128
    
    def get_pixel_y(self):
        return self.my // 128

class Controller():
    def __init__(self):
        self.right_axis = [0, 0]
        self.left_axis = [0, 0]
        self.right_point = [0, 0]
        self.deadzone = 0

    def press_button(self, code, is_pressed): print("PRESS: ", code, is_pressed)
    def press_pad(self, direction, is_pressed): print("PRESS PAD", direction, is_pressed)
    def move_joystick(self, joystick, direction, precent): print("MOVE JOYSTICK", joystick, direction, precent)
    def move_trigger(self, direction, precent): print("MOVE TRIGGER", direction, precent)
    
    def set_press_button(self, func):
        self.press_button = func

    def set_press_pad(self, func):
        self.press_pad = func

    def set_move_joystick(self, func):
        self.move_joystick = func
    
    def set_move_trigger(self, func):
        self.move_trigger = func
    
mouse = Mouse()
manager = Manager()
controller = Controller()

def loop():
    global mouse, controller, manager
    while manager.running:
        byte = file_in.read(16)
        m = mtype, mcode, mvalue = struct.unpack_from('hhi', byte, offset=8)

        if mtype == MOUSE_BUTTON_TYPE and mvalue == MOUSE_PRESS_VALUE:
            if mcode == MOUSE_LEFT_CLICK_CODE:
                mouse.left_click_func()
            if mcode == MOUSE_RIGHT_CLICK_CODE:
                mouse.right_click_func()
        if mtype == MOUSE_MOVE_TYPE and mcode == MOUSE_SCROLL_CODE:
            if mvalue == MOUSE_SCROLL_UP_VALUE:
                mouse.scroll_up_func()
            if mvalue == MOUSE_SCROLL_DOWN_VALUE:
                mouse.scroll_down_func()
        if mtype == MOUSE_MOVE_TYPE:
            if mcode == MOUSE_MOVE_RL_CODE:
                mouse.mx = max(min(mouse.mx + mvalue, mouse.w), 0)
            if mcode == MOUSE_MOVE_UD_CODE:
                mouse.my = max(min(mouse.my + mvalue, mouse.h), 0)
            mouse.move_func()
        if mtype == CONTROLLER_BUTTON_TYPE:
            if mcode == CONTROLLER_A_CODE:
                controller.press_button("A", True if mvalue == 1 else False)
            if mcode == CONTROLLER_B_CODE:
                controller.press_button("B", True if mvalue == 1 else False)
            if mcode == CONTROLLER_Y_CODE:
                controller.press_button("Y", True if mvalue == 1 else False)
            if mcode == CONTROLLER_X_CODE:
                controller.press_button("X", True if mvalue == 1 else False)
            if mcode == CONTROLLER_LB_CODE:
                controller.press_button("LB", True if mvalue == 1 else False)
            if mcode == CONTROLLER_RB_CODE:
                controller.press_button("RB", True if mvalue == 1 else False)
            if mcode == CONTROLLER_PRESS_LEFT_JOYSTICK_CODE:
                controller.press_button("LJ", True if mvalue == 1 else False)
            if mcode == CONTROLLER_PRESS_RIGHT_JOYSTICK_CODE:
                controller.press_button("RJ", True if mvalue == 1 else False)
        if mtype == CONTROLLER_MOVE_TYPE:
            if mcode == CONTROLLER_PAD_RL_CODE:
                if mvalue == 0:
                    controller.press_pad("R", False)
                    controller.press_pad("L", False)
                else:
                    controller.press_pad("R" if mvalue > 0 else "L", True)
            if mcode == CONTROLLER_PAD_UD_CODE:
                if mvalue == 0:
                    controller.press_pad("U", False)
                    controller.press_pad("D", False)
                else:
                    controller.press_pad("D" if mvalue > 0 else "U", True)
            if mcode in CONTROLLER_RJ_CODES:
                if abs(mvalue) > controller.deadzone:
                    if mcode % 2 == 0:
                        controller.right_axis[0] = mvalue
                        controller.move_joystick("R", "X", mvalue / 32767)
                    else:
                        controller.right_axis[1] = mvalue
                        controller.move_joystick("R", "Y", mvalue / 32767)
            if mcode in CONTROLLER_LJ_CODES:
                if abs(mvalue) > controller.deadzone:
                    if mcode % 2 == 0:
                        controller.right_axis[0] = mvalue
                        controller.move_joystick("L", "X", mvalue / 32767)
                    else:
                        controller.right_axis[1] = mvalue
                        controller.move_joystick("L", "Y", mvalue / 32767)
            if mcode == CONTROLLER_RT_CODE:
                controller.move_trigger("R", mvalue / 255)
            if mcode == CONTROLLER_LT_CODE:
                controller.move_trigger("L", mvalue / 255)
            
threading.Thread(target=loop).start()
    