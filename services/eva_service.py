from models.eva_models import PreparedEva


class EvaService:
    def add_prepared_eva(
            self,
            prepared_evas: list[PreparedEva],
            eva_name: str,
            articles: list[str],
    ) -> None:

        normalized_name = eva_name.strip()

        unique_articles = list(
            dict.fromkeys(articles)
        )

        for prepared_eva in prepared_evas:
            if (
                    prepared_eva.name.casefold()
                    == normalized_name.casefold()
            ):
                for article in unique_articles:
                    if article not in prepared_eva.articles:
                        prepared_eva.articles.append(
                            article
                        )

                return

        prepared_evas.append(
            PreparedEva(
                name=normalized_name,
                articles=unique_articles,
            )
        )