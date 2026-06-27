"""
Seed the database with healthy and adversarial synthetic examples.

Run with: python -m clinaiqa.data.seed_db
Requires the Docker Compose stack to be up and migrations applied.
Safe to run multiple times: existing rows are cleared first.
"""

import sys

from sqlalchemy import create_engine, delete, text
from sqlalchemy.orm import Session

from clinaiqa.data.generate_adversarial import generate_adversarial_examples
from clinaiqa.data.generate_healthy import generate_healthy_examples
from clinaiqa.data.schemas import AdversarialExample as AdversarialSchema
from clinaiqa.data.schemas import HealthyExample as HealthySchema
from clinaiqa.data.split import assign_split
from clinaiqa.db.models import AdversarialExample, HealthyExample
from clinaiqa.settings import settings


def seed(engine) -> dict:
    healthy_schemas: list[HealthySchema] = generate_healthy_examples()

    with Session(engine) as session:
        session.execute(delete(AdversarialExample))
        session.execute(delete(HealthyExample))
        session.commit()

        db_healthy: list[HealthyExample] = []
        for h in healthy_schemas:
            row = HealthyExample(
                doc_type=h.doc_type.value,
                source_record=h.source_record,
                output_text=h.output_text,
            )
            session.add(row)
        session.flush()

        db_healthy = session.query(HealthyExample).all()
        healthy_db_ids = [row.id for row in db_healthy]

        adversarial_schemas: list[AdversarialSchema] = generate_adversarial_examples(
            healthy_schemas, healthy_db_ids
        )
        adversarial_schemas = assign_split(adversarial_schemas)

        for a in adversarial_schemas:
            row = AdversarialExample(
                healthy_example_id=a.healthy_example_id,
                output_text=a.output_text,
                archetype=a.archetype.value,
                defect_span=a.defect_span,
                expected_flag_type=a.expected_flag_type.value,
                split_assignment=a.split_assignment.value,
                split_seed=a.split_seed,
            )
            session.add(row)
        session.commit()

        n_healthy = session.query(HealthyExample).count()
        n_tuning = (
            session.query(AdversarialExample)
            .filter(AdversarialExample.split_assignment == "tuning")
            .count()
        )
        n_heldout = (
            session.query(AdversarialExample)
            .filter(AdversarialExample.split_assignment == "heldout")
            .count()
        )

    return {"healthy": n_healthy, "tuning": n_tuning, "heldout": n_heldout}


def main() -> None:
    url = settings.database_url_sync
    if not url:
        print("ERROR: DATABASE_URL_SYNC is not set.", file=sys.stderr)
        sys.exit(1)

    engine = create_engine(url, echo=False)
    counts = seed(engine)
    print(f"Seed complete.")
    print(f"  Healthy examples:    {counts['healthy']}")
    print(f"  Adversarial tuning:  {counts['tuning']}")
    print(f"  Adversarial heldout: {counts['heldout']}")
    print(f"  Split seed: {settings.split_seed}")
    print(f"  Heldout fraction: {settings.heldout_fraction}")


if __name__ == "__main__":
    main()
