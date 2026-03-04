from abc import ABC, abstractmethod


class BaseAgent(ABC):
    name: str
    autonomy_level: str
    confidence_threshold: float = 0.8

    @abstractmethod
    async def perceive(self) -> dict: ...

    @abstractmethod
    async def reason(self, data: dict) -> dict: ...

    @abstractmethod
    async def plan(self, analysis: dict) -> list: ...

    @abstractmethod
    async def act(self, action: dict) -> dict: ...

    @abstractmethod
    async def verify(self, result: dict) -> bool: ...

    async def learn(self, outcome: dict) -> None:
        pass

    async def report(self, log: dict) -> None:
        pass

    async def run_cycle(self) -> None:
        data = await self.perceive()
        if not data:
            return
        analysis = await self.reason(data)
        actions = await self.plan(analysis)
        for action in actions:
            result = await self.act(action)
            await self.verify(result)
            await self.learn({"action": action, "result": result})
            await self.report({"agent": self.name, "action": action, "result": result})
