# MAMORX: A Multi-agent Multi-Modal Scientific Review Generation with External Knowledge

## Authors  
Pawin Taechoyotin<sup>\*</sup>, Guanchao Wang<sup>\*</sup>, Tong Zeng, Bradley Sides, Daniel Acuna<sup>\+</sup>

University of Colorado Boulder  

 <sup>\*</sup>Equal contribution.  
 <sup>\+</sup>Corresponding author: daniel.acuna@colorado.edu

## Abstract  
The deluge of scientific papers has made it challenging for researchers to throughly evaluate their own and others' ideas with regards to novelty and improvements. We propose MAMORX, an automated scientific review generation system that relies on multi-modal foundation models to address this challenge. MAMORX replicates key aspects of human review by integrating attention to text, figures, and citations, along with access to external knowledge sources. Compared to previous work, it takes advantage of large context windows to significantly reduce the number of agents and the processing time needed. The system relies on structured outputs and function calling to handle figures, evaluate novelty, and build general and domain-specific knowledge bases from external scholarly search systems. To test our method, we conducted an arena-style competition between several baselines and human reviews on diverse papers from general machine learning and NLP fields, calculating an Elo ratings on human preferences. MAMORX has a high win rate against human reviews and outperforms the next-best model, a multi-agent system. We share our system (the code for our system can be found at https://github.com/sciosci/mamorx-review-system and an example implementation is running at https://rev0.ai), and discuss further applications of foundation models for scientific evaluation.