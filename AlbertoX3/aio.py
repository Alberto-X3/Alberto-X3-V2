from __future__ import annotations


__all__ = (
    "Thread",
    "LockDeco",
    "GatherAnyError",
    "gather_any",
    "run_in_thread",
    "semaphore_gather",
    "run_as_task",
)


from threading import Thread as t_Thread
from asyncio import (
    AbstractEventLoop,
    Event,
    Lock,
    Semaphore,
    create_task,
    gather,
    get_running_loop,
)
from functools import partial, update_wrapper, wraps
from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from typing import Awaitable, Callable, Coroutine, Optional, NoReturn, Tuple, List


T = TypeVar("T")


class Thread(t_Thread):
    _return: Optional[T]
    _func: Callable[..., T]
    _event: Event
    _loop: AbstractEventLoop

    def __init__(self, func: Callable[..., T], loop: AbstractEventLoop):
        super().__init__()

        self._return = None
        self._func = func
        self._event = Event()
        self._loop = loop

    async def wait(self):
        await self._event.wait()
        return self._return

    def run(self) -> NoReturn:
        try:
            self._return = True, self._func()
        except Exception as e:
            self._return = False, e
        self._loop.call_soon_threadsafe(self._event.set)


class LockDeco:
    lock: Lock
    func: Callable

    def __init__(self, func):
        self.lock = Lock()
        self.func = func
        update_wrapper(self, func)

    async def __call__(self, *args, **kwargs):
        async with self.lock:
            return await self.func(*args, **kwargs)


class GatherAnyError(Exception):
    idx: int
    exception: Exception

    def __init__(self, idx: int, exception: Exception):
        self.idx = idx
        self.exception = exception


async def gather_any(*coroutines: Awaitable[T]) -> Tuple[int, T]:
    event = Event()
    res: List[Tuple[int, bool, T]] = []

    async def inner(idx: int, coro: Awaitable[T]):
        try:
            res.append((idx, True, await coro))
        except Exception as e:
            res.append((idx, False, e))
        event.set()

    tasks = [create_task(inner(i, c)) for i, c in enumerate(coroutines)]
    await event.wait()

    for task in tasks:
        if not task.done():
            task.cancel()

    index, ok, value = res[0]  # the first result
    if not ok:
        raise GatherAnyError(index, value)
    else:
        return index, value


async def run_in_thread(func, *args, **kwargs):
    thread = Thread(partial(func, *args, **kwargs), get_running_loop())
    thread.start()
    ok, result = await thread.wait()
    if not ok:
        raise result
    else:
        return result


async def semaphore_gather(n: int, /, *tasks: Coroutine) -> List:
    semaphore = Semaphore(n)

    async def inner(t):
        async with semaphore:
            return await t

    return list(await gather(*map(inner, tasks)))


def run_as_task(func: T) -> T:
    @wraps(func)
    async def inner(*args, **kwargs):
        create_task(func(*args, **kwargs))

    return inner
