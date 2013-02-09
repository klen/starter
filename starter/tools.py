def flatten(e):
    try:
        while True:
            yield next(e)

    except TypeError:
        yield e

    except StopIteration:
        pass

    # for e in iterable:
        # try:
            # while True:
                # yield next(e)

        # except TypeError:
            # yield e

        # except StopIteration:
            # continue
