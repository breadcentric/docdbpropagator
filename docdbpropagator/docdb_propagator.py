import yaml

from docdbpropagator.config_validator import ConfigValidator
from .collection_report_generator import CollectionReportGenerator
from .mongo_data_generator import MongoDataGenerator


def determine_collection_name(config, collection_name, collection_suffix):
    return collection_name if collection_name else (
            config['collection_name'] + (f"_{collection_suffix}" if collection_suffix else ""))


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Generate and insert data into MongoDB')
    parser.add_argument('--config-file', default='examples/sample_config.yaml', dest="config_file", help='Path to config file')
    parser.add_argument('--mongodb-uri', default='mongodb://localhost:27017', dest="mongodb_uri", help='MongoDB URI')
    parser.add_argument('--database', default='test_db', help='Database name')
    parser.add_argument('--suffix', default='', help='Suffix to be added to the collection name')
    parser.add_argument('--collection', default='', help='Collection name (overrides the file config)')
    parser.add_argument('--count', type=int, default=1000, help='Number of records to insert')
    parser.add_argument('--report', action='store_true', dest='report',
                        help='Print values report instead of inserting values')
    parser.add_argument('--skip-report', action='store_true', dest='skip_report',
                        help='Print values report instead of inserting values')
    parser.add_argument('--dress-rehearsal', action='store_true', dest='dress_rehearsal',
                        help='Print records to stdout instead of inserting into MongoDB')

    args = parser.parse_args()

    with open(args.config_file, 'r') as file:
        config = yaml.safe_load(file)

    validator = ConfigValidator()
    config = validator.validate_dict(config)

    collection_name = determine_collection_name(config, args.collection, args.suffix)

    if not args.report:
        generator = MongoDataGenerator(config, collection_name)

        print(f"{'Inserting' if not args.dress_rehearsal else 'Generating'} {args.count} records to {generator.collection_name} in {args.database}")

        records_inserted = generator.insert_records(
            mongodb_uri=args.mongodb_uri,
            database_name=args.database,
            count=args.count,
            dress_rehearsal=args.dress_rehearsal
        )

        action = "processed" if args.dress_rehearsal else "inserted"
        print(f"Successfully {action} {records_inserted} records to {generator.collection_name} in {args.database}")

    if not args.skip_report and not args.dress_rehearsal:
        report_generator = CollectionReportGenerator(args.mongodb_uri, args.database, collection_name)
        report_generator.analyze_field_coverage()


if __name__ == "__main__":
    main()



