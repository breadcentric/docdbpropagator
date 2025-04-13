import io
import sys
import unittest
from docdbpropagator.mongo_data_generator import MongoDataGenerator


class TestMongoDataGenerator(unittest.TestCase):
    def setUp(self):
        self.sample_config = {
            'fields': [
                {
                    'name': 'test_field',
                    'type': 'string',
                    'specs': {
                        'length_range': [5, 10]
                    }
                }
            ]
        }

    def test_dress_rehearsal_mode(self):
        # Redirect stdout to capture print statements
        captured_output = io.StringIO()
        sys.stdout = captured_output

        try:
            generator = MongoDataGenerator(self.sample_config, 'test_collection')
            records_processed = generator.insert_records(
                mongodb_uri='mongodb://dummy',
                database_name='test_db',
                count=2,
                dress_rehearsal=True
            )

            output = captured_output.getvalue()
            
            # Check that the correct number of records were processed
            self.assertEqual(records_processed, 2)

            lines = output.split('\n')
            
            # Check that records were printed to stdout
            self.assertIn('\'test_field\':', lines[0])
            self.assertIn('\'test_field\':', lines[1])
            
            # Check that no MongoDB connection was attempted
            self.assertNotIn('Inserted', lines[2])
            
        finally:
            # Restore stdout
            sys.stdout = sys.__stdout__


if __name__ == '__main__':
    unittest.main()