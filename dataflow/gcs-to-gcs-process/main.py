import apache_beam as beam
from apache_beam.io.textio import ReadFromText, WriteToText
from apache_beam.options.pipeline_options import PipelineOptions



def read_and_write_with_cloud_storage(argv=None):
    # Parse the pipeline options passed into the application.
    class MyOptions(PipelineOptions):
        @classmethod
        # Define a custom pipeline option that specfies the Cloud Storage bucket.
        def _add_argparse_args(cls, parser):
            parser.add_argument("--input",required=True)
            parser.add_argument("--output", required=True)

    options = MyOptions()

    with beam.Pipeline(options=options) as pipeline:
        (
            pipeline
            | "Create elements" >> ReadFromText(options.input)
            | "Write Files" >> WriteToText(options.output, file_name_suffix=".txt")
        )


if __name__ == "__main__":
    read_and_write_with_cloud_storage()