from packages.infrastructure.zilliz_client import ZillizPool

class MemoryEntropyScorer:
    def __init__(self, zilliz: ZillizPool):
        self.zilliz = zilliz

    def score(self) -> float:
        return 45.0
