import asyncio
import logging

logger = logging.getLogger('task')


def task_exception(coro):
    async def wrapper(*args, **kwargs):
        try:
            await coro(*args, **kwargs)
        except Exception:
            logger.error(f"Task {coro} failed", exc_info=True)
    return wrapper


@task_exception
async def common_loop(
    method,
    init_coro=None,
    sleep=None,
    log=None
) -> None:
    if log is None:
        log = logger

    if init_coro:
        await init_coro

    while True:
        try:
            await method()
            if sleep:
                await asyncio.sleep(sleep)
        except asyncio.CancelledError:
            log.info(f"Cancelled {method.__name__}, stopping task")
            return
        except Exception as e:
            log.error(f"Unexpected error in {method.__name__}: {e}", exc_info=True)
            await asyncio.sleep(5)
