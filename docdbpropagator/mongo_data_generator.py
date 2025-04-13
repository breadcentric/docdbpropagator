import random
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, Iterator, List

import pymongo
from bson import Decimal128


class MongoDataGenerator:
    def __init__(self, config: Dict[str, Any], collection_name: str):
        self.batch_size = 1000
        self.collection_name = collection_name
        self.fields = config['fields']

    @staticmethod
    def generate_value(field_type: str, specs: Any) -> Any:
        # Check for null first
        if 'null_probability' in specs and \
                random.random() < specs['null_probability']:
            return None

        # If values are provided, pick one randomly regardless of type
        if 'values' in specs and field_type != 'array':
            return random.choice(specs['values'])

        if field_type == 'big_integer':
            return random.randint(specs['range'][0], specs['range'][1])

        elif field_type == 'big_decimal':
            min_val = Decimal(str(specs['range'][0]))
            max_val = Decimal(str(specs['range'][1]))
            range_size = max_val - min_val
            random_decimal = min_val + (Decimal(random.random()) * range_size)
            return Decimal128(round(random_decimal, specs.get('precision', 2)))

        elif field_type == 'string':
            length = random.randint(
                specs['length_range'][0],
                specs['length_range'][1]
            )
            return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=length))

        elif field_type == 'boolean':
            return random.random() < specs.get('true_probability', 0.5)

        elif field_type == 'datetime':
            start_date = datetime.fromisoformat(specs['range'][0])
            end_date = datetime.fromisoformat(specs['range'][1])
            time_between = end_date - start_date
            random_seconds = random.randint(0, int(time_between.total_seconds()))
            return start_date + timedelta(seconds=random_seconds)

        elif field_type == 'array':
            size = random.randint(
                specs['size_range'][0],
                specs['size_range'][1]
            )

            if 'element_type' in specs:
                return [
                    MongoDataGenerator.generate_value(specs['element_type'], specs['element_specs'])
                    for _ in range(size)
                ]

            if 'values' not in specs:
                return []

            return random.sample(specs['values'], size)

    def generate_record(self) -> Dict[str, Any]:
        record = {}
        for field in self.fields:
            field_type = field['type']
            specs = field['specs']
            generated_value = self.generate_value(field_type, specs)
            if generated_value is not None:
                record[field['name']] = generated_value
        return record

    def generate_records(self, count: int) -> Iterator[List[Dict[str, Any]]]:
        """Generates records in batches.

        Args:
            count: Total number of records to generate

        Yields:
            List of dictionaries containing generated records
        """
        batch = []
        for i in range(count):
            batch.append(self.generate_record())
            if len(batch) >= self.batch_size:
                yield batch
                batch = []

        # Don't forget remaining records
        if batch:
            yield batch

    def insert_records(self, mongodb_uri: str, database_name: str, count: int, dress_rehearsal: bool = False):
        """Insert records into MongoDB or print them to stdout in dress rehearsal mode.

        Args:
            mongodb_uri: MongoDB connection URI
            database_name: Name of the database
            count: Number of records to generate
            dress_rehearsal: If True, prints records to stdout instead of inserting to MongoDB

        Returns:
            int: Number of records processed
        """
        if dress_rehearsal:
            total_processed = 0
            for batch in self.generate_records(count):
                for record in batch:
                    print(f"Record {total_processed + 1}: {record}")
                total_processed += len(batch)
                if (total_processed * 0.01) / count >= 0.1:  # Print progress every 10%
                    print(f"Processed {(total_processed * 100.0) / count}% of records")
            return total_processed
        
        with pymongo.MongoClient(mongodb_uri) as client:
            db = client[database_name]
            collection = db[self.collection_name]

            total_inserted = 0
            next_percentage_to_report = 10
            for batch in self.generate_records(count):
                collection.insert_many(batch)
                total_inserted += len(batch)
                if (total_inserted * 0.01) / count >= next_percentage_to_report / 100.0:
                    print(f"Inserted {(total_inserted * 0.01) / count}% of records")
                    next_percentage_to_report += 10

        return total_inserted

