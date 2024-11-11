import logging
from collections import OrderedDict
from typing import Dict, List

from pydantic import BaseModel

from ai_reviewer_arena.configs.logging_cfg import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger("ModelRegistry")


class ReviewerInfo(BaseModel):
    id: str
    short_name: str
    long_name: str
    link: str
    description: str


class ReviewerRegistry:
    def __init__(self):
        self.model_info: Dict[str, ReviewerInfo] = OrderedDict()
        logger.info("Initialized ModelRegistry")

    def register_model_info(
        self, id: str, short_name: str, long_name: str, link: str, description: str
    ):
        info = ReviewerInfo(
            id=id,
            short_name=short_name,
            long_name=long_name,
            link=link,
            description=description,
        )
        self.model_info[id] = info
        logger.info(f"Registered model info: {info}")

    def get_model_info(self, id: str) -> ReviewerInfo:
        if id in self.model_info:
            logger.info(f"Retrieved model info for id: {id}")
            return self.model_info[id]
        else:
            logger.error(f"Model {id} does not exist")
            raise Exception(
                f"The model {id} does not exist. Please use `register_model_info` to register the model."
            )

    def get_model_id_list(self) -> List[str]:
        logger.info("Retrieved list of all registered model ids")
        return list(self.model_info.keys())

    def get_model_description_md(self) -> str:
        logger.info("Generating markdown description for all models")
        model_description_md = """
| | | |
| ---- | ---- | ---- |
"""
        ct = 0
        visited = set()
        for id in self.model_info:
            info = self.get_model_info(id)
            if info.short_name in visited:
                continue
            visited.add(info.short_name)
            one_model_md = f"[{info.short_name} ({info.long_name})]({info.link}): {info.description}"

            if ct % 3 == 0:
                model_description_md += "|"
            model_description_md += f" {one_model_md} |"
            if ct % 3 == 2:
                model_description_md += "\n"
            ct += 1
        return model_description_md

    def get_all_short_names(self) -> List[str]:
        """Returns a list of all registered model short names."""
        logger.info("Retrieved list of all registered model short names")
        return [info.short_name for info in self.model_info.values()]

    def get_short_name(self, id: str) -> str:
        """Returns the short name for a specified model id."""
        info = self.get_model_info(id)
        logger.info(f"Retrieved short name for model id: {id}")
        return info.short_name

    def get_all_long_names(self) -> List[str]:
        """Returns a list of all registered model long names."""
        logger.info("Retrieved list of all registered model long names")
        return [info.long_name for info in self.model_info.values()]

    def get_long_name(self, id: str) -> str:
        """Returns the long name for a specified model id."""
        info = self.get_model_info(id)
        logger.info(f"Retrieved long name for model id: {id}")
        return info.long_name


# Example usage:
model_registry = ReviewerRegistry()

model_registry.register_model_info(
    id="human_reviewer",
    short_name="Human Reviewer",
    long_name="Human Reviewer",
    link="http://example.com/model_v1",
    description="These reviews are get from OpenView",
)

model_registry.register_model_info(
    id="barebones",
    short_name="Barebones Model",
    long_name="Barebones Model",
    link="http://example.com/A",
    description="Paper authored by barebones",
)

model_registry.register_model_info(
    id="liang_etal",
    short_name="Liang Etal",
    long_name="liang_etal",
    link="http://example.com/B",
    description="Paper authored by barebones",
)

model_registry.register_model_info(
    id="multi_agent_without_knowledge",
    short_name="Multi Agent without Knowledge",
    long_name="Multi Agent without Knowledge",
    link="http://example.com/C",
    description="Our paper - multi agent without knowledge",
)
