/* Ensure pad events are enabled and trace a bounded sample before Python. */
#include <SDL.h>
#include <stdio.h>

SDL_GameController *__real_SDL_GameControllerOpen(int index);
static unsigned int traced;
static int watching;

static int trace_pad_event(void *unused, SDL_Event *event)
{
    (void)unused;
    if (traced >= 32)
        return 1;
    if (event->type == SDL_CONTROLLERBUTTONDOWN || event->type == SDL_CONTROLLERBUTTONUP) {
        ++traced;
        fprintf(stderr, "SDL pad: type=%u id=%d button=%u state=%u\n",
            event->type, event->cbutton.which, event->cbutton.button, event->cbutton.state);
    } else if (event->type == SDL_JOYBUTTONDOWN || event->type == SDL_JOYBUTTONUP) {
        ++traced;
        fprintf(stderr, "SDL joystick: type=%u id=%d button=%u state=%u\n",
            event->type, event->jbutton.which, event->jbutton.button, event->jbutton.state);
    }
    return 1;
}

SDL_GameController *__wrap_SDL_GameControllerOpen(int index)
{
    SDL_GameController *pad = __real_SDL_GameControllerOpen(index);
    if (pad) {
        SDL_JoystickEventState(SDL_ENABLE);
        SDL_GameControllerEventState(SDL_ENABLE);
        if (!watching) {
            SDL_AddEventWatch(trace_pad_event, NULL);
            watching = 1;
        }
        fprintf(stderr, "SDL pad opened: index=%d joystick_events=%d controller_events=%d\n",
            index, SDL_JoystickEventState(SDL_QUERY), SDL_GameControllerEventState(SDL_QUERY));
    }
    return pad;
}
