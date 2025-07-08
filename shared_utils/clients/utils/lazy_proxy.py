class LazyProxy:
    """A lazy proxy that delays the instantiation of an object until its attributes are accessed."""
    
    def __init__(self, factory):
        self._factory = factory
        self._instance = None

    def _load(self):
        if self._instance is None:
            self._instance = self._factory()
        return self._instance

    def __getattr__(self, name):
        return getattr(self._load(), name)

    def __setattr__(self, name, value):
        if name in {"_factory", "_instance"}:
            super().__setattr__(name, value)
        else:
            setattr(self._load(), name, value)
