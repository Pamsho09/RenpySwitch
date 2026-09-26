"""Switch Lite display defaults and optional controller shortcuts."""
_previous_map = None
_held = set()
_triggers = set()
_original_post_event = None
_input_log_count = 0


def map_pad_event(name):
    import renpy
    if name.endswith('_press'):
        _held.add(name[:-6])
    elif name.endswith('_release'):
        _held.discard(name[:-8])

    for trigger in ('pad_lefttrigger', 'pad_righttrigger'):
        if name == trigger + '_pos':
            _triggers.add(trigger)
            return ['skip']
        if name in (trigger + '_zero', trigger + '_neg'):
            _triggers.discard(trigger)
            return [] if _triggers else ['stop_skipping']
        if name == 'repeat_' + trigger + '_pos':
            return []

    # SDL maps physical Switch X to the logical Y button.
    if (name == 'pad_y_press' and
            {'pad_leftshoulder', 'pad_rightshoulder'} <= _held and
            hasattr(getattr(renpy.store, 'x52URM', None), 'Open')):
        return ['alt_K_m']
    if _previous_map is not None:
        return _previous_map(name)
    return renpy.config.pad_bindings.get(name, ())


def apply():
    global _previous_map, _original_post_event
    import renpy
    preferences = renpy.game.preferences
    preferences.physical_size = (1280, 720)
    preferences.fullscreen = False
    preferences.maximized = False
    preferences.gl_framerate = 30
    preferences.pad_enabled = 'all'
    renpy.config.save_physical_size = False
    if renpy.config.map_pad_event is not map_pad_event:
        _previous_map = renpy.config.map_pad_event
        renpy.config.map_pad_event = map_pad_event
    if renpy.display.controller.post_event is not post_event:
        _original_post_event = renpy.display.controller.post_event
        renpy.display.controller.post_event = post_event
    _held.clear()
    _triggers.clear()
    renpy.exports.write_log('Switch Lite profile: 1280x720, 30 FPS target; ZL/ZR hold to skip; optional URM L+R+X')


def post_event(control, state, repeat):
    """Console pad events do not require desktop keyboard window focus."""
    global _input_log_count
    import renpy
    interface = renpy.display.interface
    focused = interface.keyboard_focused
    if not repeat and _input_log_count < 32:
        renpy.exports.write_log('Switch input: %s %s keyboard_focus=%s' % (control, state, focused))
        _input_log_count += 1
    interface.keyboard_focused = True
    try:
        return _original_post_event(control, state, repeat)
    finally:
        interface.keyboard_focused = focused
