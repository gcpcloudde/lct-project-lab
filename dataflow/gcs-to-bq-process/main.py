import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions
from typing import NamedTuple
import csv
import logging


# Define the schema using NamedTuple
class TaxiRecord(NamedTuple):
    VendorID: int
    tpep_pickup_datetime: str
    tpep_dropoff_datetime: str
    passenger_count: int
    trip_distance: float
    RatecodeID: int
    store_and_fwd_flag: str
    PULocationID: int
    DOLocationID: int
    payment_type: int
    fare_amount: float
    extra: float
    mta_tax: float
    tip_amount: float
    tolls_amount: float
    improvement_surcharge: float
    total_amount: float


# BigQuery schema
bq_schema = {
    "fields": [
        {"name": "VendorID", "type": "INTEGER"},
        {"name": "tpep_pickup_datetime", "type": "TIMESTAMP"},
        {"name": "tpep_dropoff_datetime", "type": "TIMESTAMP"},
        {"name": "passenger_count", "type": "INTEGER"},
        {"name": "trip_distance", "type": "FLOAT"},
        {"name": "RatecodeID", "type": "INTEGER"},
        {"name": "store_and_fwd_flag", "type": "STRING"},
        {"name": "PULocationID", "type": "INTEGER"},
        {"name": "DOLocationID", "type": "INTEGER"},
        {"name": "payment_type", "type": "INTEGER"},
        {"name": "fare_amount", "type": "FLOAT"},
        {"name": "extra", "type": "FLOAT"},
        {"name": "mta_tax", "type": "FLOAT"},
        {"name": "tip_amount", "type": "FLOAT"},
        {"name": "tolls_amount", "type": "FLOAT"},
        {"name": "improvement_surcharge", "type": "FLOAT"},
        {"name": "total_amount", "type": "FLOAT"},
    ]
}


# CSV Parser DoFn
class ParseCSVLine(beam.DoFn):
    def __init__(self, header):
        self.header = header

    def process(self, element): 
        try:
            row = next(csv.DictReader([element], fieldnames=self.header))
            record = TaxiRecord(
                VendorID=int(row['VendorID']),
                tpep_pickup_datetime=row['tpep_pickup_datetime'],
                tpep_dropoff_datetime=row['tpep_dropoff_datetime'],
                passenger_count=int(row['passenger_count']),
                trip_distance=float(row['trip_distance']),
                RatecodeID=int(row['RatecodeID']),
                store_and_fwd_flag=row['store_and_fwd_flag'],
                PULocationID=int(row['PULocationID']),
                DOLocationID=int(row['DOLocationID']),
                payment_type=int(row['payment_type']),
                fare_amount=float(row['fare_amount']),
                extra=float(row['extra']),
                mta_tax=float(row['mta_tax']),
                tip_amount=float(row['tip_amount']),
                tolls_amount=float(row['tolls_amount']),
                improvement_surcharge=float(row['improvement_surcharge']),
                total_amount=float(row['total_amount']),
            )
            yield record._asdict()
        except Exception as e:
            logging.warning(f"Invalid row: {element} | Error: {e}")
            yield beam.pvalue.TaggedOutput("invalid", {"raw_line": element})


# Pipeline runner
def run(argv=None,save_main_session=True):  
    # Parse the pipeline options passed into the application.
    class MyOptions(PipelineOptions):
        @classmethod
        # Define a custom pipeline option that specfies the Cloud Storage bucket.
        def _add_argparse_args(cls, parser):
            parser.add_argument('--input', required=True)
            parser.add_argument('--output_table', required=True)
            parser.add_argument('--invalid_table', required=True)

    header = ['VendorID','tpep_pickup_datetime','tpep_dropoff_datetime','passenger_count','trip_distance',
              'RatecodeID','store_and_fwd_flag','PULocationID','DOLocationID','payment_type','fare_amount',
              'extra','mta_tax','tip_amount','tolls_amount','improvement_surcharge','total_amount']
    pipeline_options = PipelineOptions(argv)
    pipeline_options.view_as(SetupOptions).save_main_session = save_main_session
    options = pipeline_options.view_as(MyOptions)  

    with beam.Pipeline(options=options) as p:
        lines = p | "ReadFromGCS" >> beam.io.ReadFromText(options.input, skip_header_lines=1)

        parsed = lines | "ParseCSV" >> beam.ParDo(ParseCSVLine(header)).with_outputs("invalid", main="valid")

        valid_rows = parsed.valid
        invalid_rows = parsed.invalid

        valid_rows | "WriteToBQValid" >> beam.io.WriteToBigQuery(
            options.output_table,
            schema=bq_schema,
            write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
            create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED
        )

        invalid_rows | "WriteToBQInvalid" >> beam.io.WriteToBigQuery(
            options.invalid_table,
            schema='raw_line:STRING',
            write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
            create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED
        )


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()
