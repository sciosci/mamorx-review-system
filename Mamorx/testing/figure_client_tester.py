import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from MAMORX.schemas import APIConfigs
from MAMORX.utils.figure_critic import FigureCriticClient

def do_figure_critic(figure_critic_client: FigureCriticClient):
    pdf = "test.pdf"
    test_title = "Modeling Content and Context with Deep Relational Learning"
    test_abstract = """
    Building models for realistic natural language tasks requires dealing with long texts and accounting for complicated structural dependencies. 
    Neural-symbolic representations have emerged as a way to combine the reasoning capabilities of symbolic methods, with the
    expressiveness of neural networks. However,most of the existing frameworks for combining neural and symbolic representations have been
    designed for classic relational learning tasks that work over a universe of symbolic entities and relations. In this paper, we present DRAIL,
    an open-source declarative framework for specifying deep relational models, designed to support a variety of NLP scenarios. Our frame-
    work supports easy integration with expressive language encoders, and provides an interface to study the interactions between representation,
    inference and learning.
    """

    result = figure_critic_client.critic_pdf_file(
        pdf_file_path=pdf,
        title=test_title,
        abstract=test_abstract
    )

    print(result)


def main():
    api_config: APIConfigs = {
        "figure_critic_url": "localhost:5001"
    }

    figure_critic_client = FigureCriticClient(
        api_config=api_config
    )

    do_figure_critic(figure_critic_client)
    
    
if __name__ == "__main__":
    main()