# Optional Switch compatibility hook; the URM archive is supplied separately.
# Run before URM's init 999 automatic update check.
init 998 python:
    import sys as _switch_urm_sys
    if _switch_urm_sys.platform == "switch":
        import switch_profile as _switch_urm_profile
        _switch_urm_mod = getattr(renpy.store, "x52URM", None)
        if _switch_urm_mod is not None and hasattr(_switch_urm_mod, "API"):
            _switch_urm_mod.API.fetchUpdate = _switch_urm_profile.skip_urm_update
