from typing import Dict, Any

import pymongo


class CollectionReportGenerator:
    def __init__(self, mongodb_uri: str, database_name: str, collection_name: str):
        self.mongodb_uri = mongodb_uri
        self.database_name = database_name
        self.collection_name = collection_name

    def analyze_field_coverage(self) -> Dict[str, Dict[str, Any]]:
        """
        Analyze the field coverage in a MongoDB collection and return statistics.
        
        Returns:
            Dict[str, Dict[str, Any]]: A dictionary containing field coverage statistics
            with counts and percentages.
        """
        print(f"Gathering a report for a collection")

        with pymongo.MongoClient(self.mongodb_uri) as client:
            db = client[self.database_name]
            collection = db[self.collection_name]

            # First, get total count of documents
            total_docs = collection.count_documents({})

            # Get all possible field names from the collection
            # We'll use the first 1000 documents as a sample to find field names
            all_fields = set()
            for doc in collection.find().limit(1000):
                all_fields.update(doc.keys())

            # Create the aggregation pipeline
            pipeline = [
                {
                    "$group": {
                        "_id": None,
                        **{
                            field: {
                                "$sum": {
                                    "$cond": [
                                        {"$or": [{"$ifNull": [f"${field}", False]}, {"$eq": [f"${field}", False]}]},
                                        1,
                                        0
                                    ]
                                }
                            }
                            for field in all_fields
                        }
                    }
                }
            ]

            result = list(collection.aggregate(pipeline))[0]
            del result['_id']  # Remove the _id field from results

            # Calculate percentages
            coverage = {
                field: {
                    'count': count,
                    'percentage': (count / total_docs) * 100
                }
                for field, count in result.items()
            }

            # Print results
            print(f"\nCollection: {self.collection_name}")
            print(f"\nTotal documents: {total_docs}")
            print("\nField coverage:")
            for field, stats in coverage.items():
                print(f"{field:20} : {stats['count']:6d} records ({stats['percentage']:6.2f}%)")

            return coverage
