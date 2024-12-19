# Content Sentiment Analyzer

This is a proof-of-concept LLM information extraction pipeline and a plotly-based dashboard to analyze sentiment; beware bugs persist in dashboard. Given a dataset of text records, the pipeline first uses an LLM to extract sentiment and sentiment meta-data, such as names of constributors that caused sentiment and how the sentiment was caused. Next, the pipeline attempts to perform entity resolution of the names of the entities identified from an entity catalog; in this proof-of-concept the entity catalog is fulfilled by the WordNet dataset. If multiple entities from the entity catalog match the name extracted by the LLM then the LLM is prompted to resolve the ambiguity given the original text context. Finally, the sentiment record is saved and semantic-indexing is performed on the matched entity to index the record with the expanded hypernyms of the entity; enabling structured data analysis on the more abstract hypernym concepts.

# Citation

To read more about this or to cite the use of this code or data:

```biblatex
@article{yae_leveraging_2024,
	title = {Leveraging large language models for word sense disambiguation},
	issn = {1433-3058},
	url = {https://doi.org/10.1007/s00521-024-10747-5},
	doi = {10.1007/s00521-024-10747-5},
	journaltitle = {Neural Computing and Applications},
	shortjournal = {Neural Computing and Applications},
	author = {Yae, Jung H. and Skelly, Nolan C. and Ranly, Neil C. and {LaCasse}, Phillip M.},
	date = {2024-12-19},
}
