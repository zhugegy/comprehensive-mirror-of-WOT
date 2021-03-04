# from pynput import keyboard
#
# # The key combination to check
# COMBINATIONS = [
#     {keyboard.Key.shift, keyboard.KeyCode(char='a')},
#     {keyboard.Key.shift, keyboard.KeyCode(char='A')}
# ]
#
# # The currently active modifiers
# current = set()
#
# def execute():
#     print ("Do Something")
#
# def on_press(key):
#     if any([key in COMBO for COMBO in COMBINATIONS]):
#         current.add(key)
#         if any(all(k in current for k in COMBO) for COMBO in COMBINATIONS):
#             execute()
#
# def on_release(key):
#     if any([key in COMBO for COMBO in COMBINATIONS]):
#         current.remove(key)
#
# with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
#     listener.join()

# from pynput import keyboard
#
# def function_1():
#     print('Function 1 activated')
#
# def function_2():
#     print('Function 2 activated')
#
# with keyboard.GlobalHotKeys({
#         '5': function_1,
#         '<alt>+<ctrl>+t': function_1,
#         '<alt>+<ctrl>+y': function_2}) as h:
#     h.join()



from pynput.keyboard import Key, KeyCode, Listener


def function_1():
    """ One of your functions to be executed by a combination """
    print('Executed function_1')


def function_2():
    """ Another one of your functions to be executed by a combination """
    print('Executed function_2')


# Create a mapping of keys to function (use frozenset as sets/lists are not hashable - so they can't be used as keys)
# Note the missing `()` after function_1 and function_2 as want to pass the function, not the return value of the function
combination_to_function = {
    frozenset([KeyCode(vk=101)]): function_1,  # shift + a
    frozenset([Key.shift, KeyCode(vk=66)]): function_2,  # shift + b
    frozenset([Key.alt_l, KeyCode(vk=71)]): function_2,  # left alt + g
}


# The currently pressed keys (initially empty)
pressed_vks = set()


def get_vk(key):
    """
    Get the virtual key code from a key.
    These are used so case/shift modifications are ignored.
    """
    return key.vk if hasattr(key, 'vk') else key.value.vk


def is_combination_pressed(combination):
    """ Check if a combination is satisfied using the keys pressed in pressed_vks """
    return all([get_vk(key) in pressed_vks for key in combination])


def on_press(key):
    """ When a key is pressed """
    vk = get_vk(key)  # Get the key's vk
    pressed_vks.add(vk)  # Add it to the set of currently pressed keys

    for combination in combination_to_function:  # Loop through each combination
        if is_combination_pressed(combination):  # Check if all keys in the combination are pressed
            combination_to_function[combination]()  # If so, execute the function


def on_release(key):
    """ When a key is released """
    vk = get_vk(key)  # Get the key's vk
    pressed_vks.remove(vk)  # Remove it from the set of currently pressed keys


with Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()