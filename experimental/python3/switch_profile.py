"""Switch Lite display defaults and optional controller shortcuts."""
_previous_map = None
_held = set()
_triggers = set()


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
    global _previous_map
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
    _held.clear()
    _triggers.clear()
    renpy.exports.write_log('Switch Lite profile: 1280x720, 30 FPS target; ZL/ZR hold to skip; optional URM L+R+X')
